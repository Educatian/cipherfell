#!/usr/bin/env python3
"""Aggregate Cipherfell session CSV exports into a study summary and re-anchor
the adaptive difficulty model from real data.

Reads every *.csv in a folder (each is one participant's in-game export), and reports:
  - pre/post knowledge scores, paired gain (t, Cohen d)
  - per-item and per-concept pre->post correctness
  - difficulty calibration (mean predicted P vs. actual clean-solve rate vs. ZPD target)
  - per-concept ability (theta) and support use (hints/missteps/time)
  - EMPIRICAL RE-ANCHORING: from the per-item `adapt` events it fits the
    difficulty of each tier by maximum likelihood and emits a paste-ready
    TIERS=[...] line, turning the (simulation-justified) anchors into
    data-justified ones. Also flags per-concept items that run harder/easier
    than their tier label predicts.

Usage:
  python analyze_sessions.py <folder-of-csvs> [--charts] [--out summary.csv] [--no-recalibrate]
Stdlib only for stats; matplotlib used for --charts if installed (optional).
"""
import argparse, csv, glob, math, os, sys
from collections import defaultdict

CONCEPTS = ("auth", "crypto", "lp", "osint", "social", "integ", "avail")
TIERS_AUTHORED = [-1.5, -0.5, 0.5, 1.5]          # must match index.html TIERS
TIERNAMES = ["Novice", "Apprentice", "Journeyman", "Master"]
ZPD_OFF = 1.0                                      # must match index.html ZPD_OFF
ZPD_TARGET = 1.0 / (1.0 + math.exp(-ZPD_OFF))     # design success target = sigmoid(ZPD_OFF) ~ 0.731

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

def parse_detail(s):
    """The events `detail` column is a space-joined key=value string."""
    out = {}
    for tok in (s or "").split():
        if "=" in tok:
            k, v = tok.split("=", 1); out[k] = v
    return out

def fnum(d, k, default=None):
    try: return float(d.get(k, ""))
    except (TypeError, ValueError): return default

def mean(xs): return sum(xs) / len(xs) if xs else float("nan")
def sd(xs):
    if len(xs) < 2: return float("nan")
    m = mean(xs); return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))

def norm_cdf(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))
def sigmoid(x): return 1.0 / (1.0 + math.exp(-x)) if x > -700 else 0.0
def logit(p):
    p = min(1 - 1e-9, max(1e-9, p)); return math.log(p / (1 - p))

def paired_test(pre, post):
    d = [b - a for a, b in zip(pre, post)]
    n = len(d)
    if n < 2: return None
    md, sdd = mean(d), sd(d)
    if sdd == 0: return {"n": n, "mean_gain": md, "t": float("inf"), "df": n - 1, "p_approx": 0.0, "cohen_dz": float("inf")}
    t = md / (sdd / math.sqrt(n))
    p = 2 * (1 - norm_cdf(abs(t)))  # normal approx (use scipy ttest_rel for exact small-n p)
    return {"n": n, "mean_gain": md, "sd_gain": sdd, "t": t, "df": n - 1, "p_approx": p, "cohen_dz": md / sdd}

# ---------------------------------------------------------------- re-anchoring
#
# Why method-of-moments and not a logistic MLE on the logged ability?
# The export logs the running Elo estimate, not the learner's true ability. When
# a tier is mis-anchored, Elo *absorbs* the error into that estimate (a learner
# who keeps failing a too-hard tier simply gets a lower theta), so per-tier
# residuals against the logged ability collapse and the difficulty error becomes
# invisible. The self-consistent fix for a DDA system is to anchor each tier so
# its *observed* clean-solve rate matches the design target P = sigmoid(ZPD_OFF):
#     d_new = d_authored + ( logit(achieved_P) - logit(target_P) )
# This is on the game's own scale, needs no latent-ability model, and drives the
# closed loop (re-anchor -> redeploy -> re-measure) toward the ZPD band. We do
# NOT claim to recover latent IRT item difficulty (Elo hides part of it); we
# claim to make each tier deliver target success.

def wilson(p, n, z=1.96):
    """Wilson 95% CI half-width-ish bounds for a proportion (small-n honest)."""
    if n == 0: return (float("nan"), float("nan"))
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

def collect_adapt(files):
    """Pull every per-item `adapt` event across all sessions: tier, concept,
    clean outcome, and the game's predicted P (pPred) at solve time."""
    rows = []
    for f in files:
        d = parse_export(f)
        for e in d["events"]:
            if e.get("type") != "adapt": continue
            det = parse_detail(e.get("detail", ""))
            try:
                tier = int(float(det["tier"])); clean = int(float(det["clean"]))
                pPred = float(det["pPred"]); concept = det.get("c", "?")
            except (KeyError, ValueError): continue
            if tier < 0 or tier >= len(TIERS_AUTHORED): continue
            rows.append({"tier": tier, "clean": clean, "pPred": pPred, "c": concept})
    return rows

def recalibrate(adapt_rows, min_n=20):
    print("\n=== Empirical re-anchoring (adapt events) ===")
    if not adapt_rows:
        print("  No `adapt` events found. (Older exports, or logging was off.)")
        print("  Re-anchoring needs the per-item event log; nothing to fit.")
        return
    print(f"  {len(adapt_rows)} solved-item observations   |   design target P = sigmoid(ZPD_OFF) = {ZPD_TARGET:.3f}\n")

    by_tier = defaultdict(list)
    for r in adapt_rows: by_tier[r["tier"]].append(r["clean"])

    print("  Tier (label)      n   achieved P [95% CI]   authored d   refit d    adjust   note")
    print("  " + "-" * 82)
    refit = list(TIERS_AUTHORED)
    adopted = []
    for t in range(len(TIERS_AUTHORED)):
        ys = by_tier.get(t)
        if not ys:
            print(f"  {t} ({TIERNAMES[t]:10s})  --   (no data)"); continue
        n = len(ys); ach = mean(ys); lo, hi = wilson(ach, n)
        # method-of-moments anchor toward the ZPD target (clamp achieved off the rails)
        ach_c = min(0.98, max(0.02, ach))
        adjust = logit(ach_c) - logit(ZPD_TARGET)
        d_new = TIERS_AUTHORED[t] + adjust
        note = ""
        if n < min_n: note = "SPARSE (kept authored)"
        else: refit[t] = round(d_new, 2); adopted.append(t)
        print(f"  {t} ({TIERNAMES[t]:10s}) {n:4d}   {ach:.2f} [{lo:.2f},{hi:.2f}]   {TIERS_AUTHORED[t]:+.2f}      {d_new:+.2f}    {adjust:+.2f}   {note}")

    print("\n  Authored : TIERS = [" + ", ".join(f"{x:+.2f}" for x in TIERS_AUTHORED) + "]")
    print("  Suggested: TIERS = [" + ", ".join(f"{x:+.2f}" for x in refit) + "]   (first-order; see caveat)")
    off = [t for t in adopted if abs(refit[t] - TIERS_AUTHORED[t]) >= 0.20]
    if not off:
        print(f"  PLACEMENT: every tier delivers near-target success ({ZPD_TARGET:.2f}). Healthy.")
    else:
        for t in off:
            sign = "too easy" if refit[t] > TIERS_AUTHORED[t] else "too hard"
            print(f"  PLACEMENT: tier {t} ({TIERNAMES[t]}) runs {sign} for who is routed there "
                  f"({abs(refit[t]-TIERS_AUTHORED[t]):.2f} logit off).")
    print("  CAVEAT: tier success is confounded by adaptive selection (changing d changes who")
    print("  lands there) and by within-session learning; treat the suggestion as one step and")
    print("  re-collect after redeploying. For an external ability anchor, see pre/post (KC) below.")

    # ---- per-concept calibration residual: observed clean vs the game's own predicted P.
    # pPred already folds in ability + tier, so the residual isolates concept difficulty.
    # Concept is orthogonal to the tier-SELECTION variable, so (unlike per-tier) this is a
    # clean signal -- but we CENTER by the grand-mean residual to strip the global shift that
    # within-session learning / selection adds to every concept equally.
    by_c = defaultdict(lambda: {"clean": [], "pred": []})
    for r in adapt_rows:
        by_c[r["c"]]["clean"].append(r["clean"]); by_c[r["c"]]["pred"].append(r["pPred"])
    raw = {c: (mean(by_c[c]["clean"]) - mean(by_c[c]["pred"])) for c in by_c if by_c[c]["clean"]}
    grand = mean(list(raw.values())) if raw else 0.0
    print("\n  Per-concept difficulty (centered residual, grand-mean removed)")
    print(f"  global shift removed = {grand:+.2f} (within-session learning / selection)")
    print("  negative centered residual = concept runs HARDER than its siblings")
    print("  concept    n   predP   clean   centered   suggest b_c   note")
    for c in CONCEPTS:
        b = by_c.get(c)
        if not b or not b["clean"]:
            print(f"  {c:8s}   --   (no data)"); continue
        n = len(b["clean"]); mc = mean(b["clean"]); mp = mean(b["pred"])
        cen = (mc - mp) - grand
        # logit nudge to remove the centered residual (positive = make item harder)
        mc_adj = min(0.98, max(0.02, mp + cen))
        b_c = logit(min(0.98, max(0.02, mp))) - logit(mc_adj)
        flag = "<-- review items" if (abs(cen) >= 0.06 and n >= min_n) else ""
        print(f"  {c:8s} {n:4d}   {mp:.2f}    {mc:.2f}    {cen:+.2f}      {b_c:+.2f}       {flag}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=".")
    ap.add_argument("--charts", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--no-recalibrate", action="store_true", help="skip empirical re-anchoring")
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
            "zpd": fnum(s, "zpd_target", ZPD_TARGET),
            "theta": {c: fnum(s, "theta_" + c) for c in CONCEPTS},
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
    for c in CONCEPTS:
        vals = [r["theta"][c] for r in rows if r["theta"][c] is not None]
        if vals: print(f"  {c:8s} theta {mean(vals):+.2f}   mastery~{100/(1+math.exp(-mean(vals))):.0f}%")

    preds = [r["predP"] for r in rows if r["predP"] is not None]
    cleans = [r["clean"] for r in rows if r["clean"] is not None]
    if preds and cleans:
        zt = rows[0]["zpd"] or ZPD_TARGET
        print(f"\nDifficulty calibration: predicted P {mean(preds):.2f}  vs  actual clean-solve {mean(cleans):.2f}  (ZPD target {zt:.2f})")

    print(f"\nSupport: hints mean {mean([r['hints'] for r in rows if r['hints'] is not None]):.1f} | "
          f"missteps {mean([r['wrong'] for r in rows if r['wrong'] is not None]):.1f} | "
          f"time {mean([r['min'] for r in rows]):.1f} min")

    if not a.no_recalibrate:
        recalibrate(collect_adapt(files))

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
        ax.set_ylim(0, len(CONCEPTS)); ax.set_ylabel(f"knowledge score (/{len(CONCEPTS)})"); ax.set_title(f"Pre vs Post (N={len(rows)})")
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "pre_post.png"), dpi=120); plt.close(fig)
        thetas = [mean([r["theta"][c] for r in rows if r["theta"][c] is not None]) for c in CONCEPTS]
        fig, ax = plt.subplots(figsize=(6, 3.5)); ax.bar(list(CONCEPTS), thetas, color="#d8a43e")
        ax.set_ylabel("ability theta"); ax.set_title("Per-concept ability"); fig.tight_layout()
        fig.savefig(os.path.join(outdir, "theta_by_concept.png"), dpi=120); plt.close(fig)
        print(f"\ncharts -> {outdir}")

if __name__ == "__main__":
    main()
