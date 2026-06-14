#!/usr/bin/env python3
"""Aggregate Cipherfell session CSV exports into a study summary.

Reads every *.csv in a folder (each is one participant's in-game export), and reports:
  - pre/post knowledge scores, paired gain (t, Cohen d)
  - per-item and per-concept pre->post correctness
  - difficulty calibration (mean predicted P vs. actual clean-solve rate vs. ZPD target)
  - per-concept ability (theta) and support use (hints/missteps/time)

Usage:
  python analyze_sessions.py <folder-of-csvs> [--charts] [--out summary.csv]
Stdlib only for stats; matplotlib used for --charts if installed (optional).
"""
import argparse, csv, glob, math, os, sys
from collections import defaultdict

def parse_export(path):
    """Parse one multi-section export -> dict(section -> rows/kv)."""
    sect = None; data = {"session": {}, "pre": [], "post": [], "events": []}
    hdr = None
    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                hdr = None; continue
            if line.startswith("#"):
                name = line.lstrip("# ").strip().lower()
                sect = ("session" if name.startswith("session") else
                        "pre" if name.startswith("pre") else
                        "post" if name.startswith("post") else
                        "events" if name.startswith("events") else None)
                hdr = None; continue
            cells = next(csv.reader([line]))
            if sect == "session":
                if cells and cells[0] == "field":  # header
                    continue
                if len(cells) >= 2:
                    data["session"][cells[0]] = cells[1]
            elif sect in ("pre", "post", "events"):
                if hdr is None:
                    hdr = cells; continue
                data[sect].append(dict(zip(hdr, cells)))
    return data

def fnum(d, k, default=None):
    try: return float(d.get(k, ""))
    except (TypeError, ValueError): return default

def mean(xs): return sum(xs) / len(xs) if xs else float("nan")
def sd(xs):
    if len(xs) < 2: return float("nan")
    m = mean(xs); return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

def norm_cdf(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def paired_test(pre, post):
    d = [b - a for a, b in zip(pre, post)]
    n = len(d)
    if n < 2: return None
    md, sdd = mean(d), sd(d)
    if sdd == 0: return {"n": n, "mean_gain": md, "t": float("inf"), "df": n - 1, "p_approx": 0.0, "cohen_dz": float("inf")}
    t = md / (sdd / math.sqrt(n))
    p = 2 * (1 - norm_cdf(abs(t)))  # normal approx (use scipy ttest_rel for exact small-n p)
    return {"n": n, "mean_gain": md, "sd_gain": sdd, "t": t, "df": n - 1, "p_approx": p, "cohen_dz": md / sdd}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=".")
    ap.add_argument("--charts", action="store_true")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(a.folder, "*.csv")))
    files = [f for f in files if "summary" not in os.path.basename(f).lower()]
    if not files: sys.exit(f"No CSVs in {a.folder!r}")

    rows = []
    pre_item = defaultdict(list); post_item = defaultdict(list); concepts = {}
    for f in files:
        d = parse_export(f); s = d["session"]
        rows.append({
            "pid": s.get("pid", ""), "won": s.get("won", ""),
            "pre": fnum(s, "pre_score"), "post": fnum(s, "post_score"),
            "hints": fnum(s, "hints"), "wrong": fnum(s, "wrong"),
            "min": (fnum(s, "play_ms", 0) or 0) / 60000.0,
            "predP": fnum(s, "mean_predP"), "clean": fnum(s, "clean_solve_rate"),
            "zpd": fnum(s, "zpd_target", 0.7),
            "theta": {c: fnum(s, "theta_" + c) for c in ("auth", "crypto", "lp", "osint", "social", "integ")},
        })
        for r in d["pre"]:
            pre_item[r.get("q", "?")].append(int(r.get("correct", "0") or 0)); concepts[r.get("q", "?")] = r.get("concept", "")
        for r in d["post"]:
            post_item[r.get("q", "?")].append(int(r.get("correct", "0") or 0))

    pre = [r["pre"] for r in rows if r["pre"] is not None]
    post = [r["post"] for r in rows if r["post"] is not None]
    paired = [(r["pre"], r["post"]) for r in rows if r["pre"] is not None and r["post"] is not None]

    print(f"\n=== Cipherfell session summary ===  N = {len(rows)} files\n")
    print(f"Pre  score: mean {mean(pre):.2f} (SD {sd(pre):.2f})  n={len(pre)}")
    print(f"Post score: mean {mean(post):.2f} (SD {sd(post):.2f})  n={len(post)}")
    if len(paired) >= 2:
        t = paired_test([p for p, _ in paired], [q for _, q in paired])
        print(f"Paired gain: +{t['mean_gain']:.2f}  (t({t['df']})={t['t']:.2f}, p~{t['p_approx']:.4f}, Cohen dz={t['cohen_dz']:.2f})")
        print("  [p is a normal approximation; use scipy.stats.ttest_rel for exact small-sample p]")

    print("\nPer-item pre->post correct rate:")
    for q in sorted(pre_item, key=lambda x: (len(x), x)):
        pr = mean(pre_item[q]); po = mean(post_item.get(q, [])) if post_item.get(q) else float("nan")
        print(f"  Q{q} {concepts.get(q,'')[:26]:26s}  pre {pr:.2f} -> post {po:.2f}")

    print("\nPer-concept ability theta (mean across learners):")
    for c in ("auth", "crypto", "lp", "osint", "social", "integ"):
        vals = [r["theta"][c] for r in rows if r["theta"][c] is not None]
        if vals: print(f"  {c:8s} theta {mean(vals):+.2f}   mastery~{100/(1+math.exp(-mean(vals))):.0f}%")

    preds = [r["predP"] for r in rows if r["predP"] is not None]
    cleans = [r["clean"] for r in rows if r["clean"] is not None]
    if preds and cleans:
        zt = rows[0]["zpd"] or 0.7
        print(f"\nDifficulty calibration: predicted P {mean(preds):.2f}  vs  actual clean-solve {mean(cleans):.2f}  (ZPD target {zt:.2f})")

    print(f"\nSupport: hints mean {mean([r['hints'] for r in rows if r['hints'] is not None]):.1f} | "
          f"missteps {mean([r['wrong'] for r in rows if r['wrong'] is not None]):.1f} | "
          f"time {mean([r['min'] for r in rows]):.1f} min")

    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["pid", "pre", "post", "gain", "hints", "wrong", "min", "predP", "clean"])
            for r in rows:
                g = (r["post"] - r["pre"]) if (r["pre"] is not None and r["post"] is not None) else ""
                w.writerow([r["pid"], r["pre"], r["post"], g, r["hints"], r["wrong"], f"{r['min']:.1f}", r["predP"], r["clean"]])
        print(f"\nwrote {a.out}")

    if a.charts:
        try:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        except ImportError:
            print("\n[--charts skipped: matplotlib not installed]"); return
        outdir = os.path.join(a.folder, "charts"); os.makedirs(outdir, exist_ok=True)
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.bar(["pre", "post"], [mean(pre), mean(post)], yerr=[sd(pre), sd(post)], color=["#b5663b", "#6b7f4e"], capsize=6)
        ax.set_ylim(0, 6); ax.set_ylabel("knowledge score (/6)"); ax.set_title(f"Pre vs Post (N={len(rows)})")
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "pre_post.png"), dpi=120); plt.close(fig)
        cs = ["auth", "crypto", "lp", "osint", "social", "integ"]
        thetas = [mean([r["theta"][c] for r in rows if r["theta"][c] is not None]) for c in cs]
        fig, ax = plt.subplots(figsize=(6, 3.5)); ax.bar(cs, thetas, color="#d8a43e")
        ax.set_ylabel("ability theta"); ax.set_title("Per-concept ability"); fig.tight_layout()
        fig.savefig(os.path.join(outdir, "theta_by_concept.png"), dpi=120); plt.close(fig)
        print(f"\ncharts -> {outdir}")

if __name__ == "__main__":
    main()
