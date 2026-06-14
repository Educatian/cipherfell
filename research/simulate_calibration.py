#!/usr/bin/env python3
"""Generate synthetic Cipherfell exports from a KNOWN-TRUTH model, so the
empirical re-anchoring in analyze_sessions.py can be validated before any real
participants exist.

The simulator mirrors the in-game adaptive loop exactly:
  - tier is chosen by pickTier(thetaG_estimate) against the AUTHORED anchors
  - pPred = sigmoid(thetaG_estimate - TIERS_authored[tier])   (logged, pre-update)
  - the learner actually succeeds with prob sigmoid(theta_true - d_TRUE[tier] - b_TRUE[concept])
  - thetaG / theta are updated by binary Elo (K=0.7), same as the game
It then writes one multi-section CSV per learner in the exact export format.

We deliberately plant: tier 2 (Journeyman) HARDER than its authored anchor, and
concept `osint` harder / `auth` easier than their tier label. A correct estimator
must recover the planted tier difficulties and flag those concepts.

Usage:
  python simulate_calibration.py --out sim_data [--learners 400] [--plays 2] [--seed 7]
Then:
  python analyze_sessions.py sim_data
and check Refit TIERS ~ the planted d_TRUE below, and osint/auth flagged.
"""
import argparse, math, os, random

CONCEPTS = ["auth", "crypto", "lp", "osint", "social", "integ", "avail"]
TIERS_AUTHORED = [-1.5, -0.5, 0.5, 1.5]      # what the game uses to pick tiers + log pPred
ZPD_OFF, ELO_K = 1.0, 0.7

# ---- planted ground truth (what analyze_sessions.py must recover) ----
D_TRUE = [-1.5, -0.5, 0.95, 1.5]             # tier 2 is really +0.95, not +0.5  -> drift +0.45
B_TRUE = {"osint": 0.60, "auth": -0.40}      # osint harder, auth easier; others 0

def sigmoid(x): return 1.0 / (1.0 + math.exp(-x)) if x > -700 else 0.0
def pick_tier(theta):
    target = theta - ZPD_OFF
    return min(range(len(TIERS_AUTHORED)), key=lambda i: abs(TIERS_AUTHORED[i] - target))

def simulate_learner(theta_true, plays, rng):
    """Returns (events, pre_score, post_score). thetaG/theta persist across plays."""
    thetaG = 0.0
    theta_c = {c: 0.0 for c in CONCEPTS}
    events = []; t = 0
    learned = 0.0  # crude learning: ability nudges up a touch each act (for pre/post realism)
    for _ in range(plays):
        for act in range(1, 8):
            c = CONCEPTS[act - 1]
            tier = pick_tier(thetaG)
            pPred = sigmoid(thetaG - TIERS_AUTHORED[tier])          # logged pre-update
            p_true = sigmoid((theta_true + learned) - D_TRUE[tier] - B_TRUE.get(c, 0.0))
            clean = 1 if rng.random() < p_true else 0
            # binary Elo updates (identical to the game)
            thetaG += ELO_K * (clean - sigmoid(thetaG - TIERS_AUTHORED[tier]))
            theta_c[c] += ELO_K * (clean - sigmoid(theta_c[c] - TIERS_AUTHORED[tier]))
            learned += 0.04
            t += rng.randint(20000, 60000)
            nxt = pick_tier(thetaG) if act < 7 else ""
            detail = (f"c={c} tier={tier} dh={0 if clean else 1} dw={0 if clean else rng.randint(1,2)} "
                      f"out={clean} pPred={pPred:.2f} clean={clean} "
                      f"thetaG={thetaG:.2f} theta={theta_c[c]:.2f} next={nxt}")
            events.append((t, act, act, "adapt", detail))
    # plausible pre/post knowledge scores out of 7 (true ability -> probability correct)
    base = sigmoid(theta_true - 0.3)
    pre = sum(1 for _ in CONCEPTS if rng.random() < base * 0.7)
    post = sum(1 for _ in CONCEPTS if rng.random() < min(0.98, base * 0.7 + 0.30))
    return events, pre, post, thetaG, theta_c

def csv_esc(v): return '"' + str(v).replace('"', '""') + '"'

def write_export(path, pid, events, pre, post, thetaG, theta_c):
    lines = ["# session", "field,value",
             f"pid,{pid}", "consent,yes", "won,1",
             f"pre_score,{pre}", f"post_score,{post}", f"delta,{post-pre}",
             "seals,7", "hints,0", "wrong,0", f"play_ms,{events[-1][0]}", "rating,1500",
             "seed,sim", f"tiers_act1to7,{'|'.join(str(pick_tier(0)) for _ in range(7))}",
             f"thetaG,{thetaG:.3f}", f"calib_n,{len(events)}", "mean_predP,0.700",
             "clean_solve_rate,0.700", "zpd_target,0.670"]
    for c in CONCEPTS:
        lines.append(f"theta_{c},{theta_c[c]:.3f}")
    lines += ["", "# pre_answers", "q,concept,picked,correct"]
    for i, c in enumerate(CONCEPTS, 1):
        lines.append(f"{i},{c},0,{1 if i <= pre else 0}")
    lines += ["", "# post_answers", "q,concept,picked,correct"]
    for i, c in enumerate(CONCEPTS, 1):
        lines.append(f"{i},{c},0,{1 if i <= post else 0}")
    lines += ["", "# events", "t_ms,act,seals,type,detail"]
    for (tm, act, seals, typ, det) in events:
        lines.append(f"{tm},{act},{seals},{typ},{csv_esc(det)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sim_data")
    ap.add_argument("--learners", type=int, default=400)
    ap.add_argument("--plays", type=int, default=2)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--tiers", default="", help="comma-sep operating anchors the GAME uses "
                    "(selection/pPred/Elo); truth stays D_TRUE. Use to validate a refit.")
    a = ap.parse_args()
    if a.tiers:
        global TIERS_AUTHORED
        TIERS_AUTHORED = [float(x) for x in a.tiers.split(",")]
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)
    for i in range(a.learners):
        theta_true = rng.gauss(0.6, 1.3)        # wide spread so all tiers get visited
        ev, pre, post, tg, tc = simulate_learner(theta_true, a.plays, rng)
        write_export(os.path.join(a.out, f"sim_{i:04d}.csv"), f"s{i:04d}", ev, pre, post, tg, tc)
    print(f"wrote {a.learners} synthetic exports -> {a.out}/")
    print("PLANTED truth:")
    print("  D_TRUE  = [" + ", ".join(f"{x:+.2f}" for x in D_TRUE) + "]   (tier 2 = +0.95, authored +0.50)")
    print("  B_TRUE  = osint +0.60 (harder), auth -0.40 (easier)")
    print(f"Now run:  python analyze_sessions.py {a.out}")

if __name__ == "__main__":
    main()
