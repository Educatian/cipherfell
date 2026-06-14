# Cipherfell — Adaptive Design & Research Instrument

This document specifies the adaptive-learning and assessment design of **Cipherfell — The Warden's Eye**, an evidence-grounded browser RPG that teaches seven cybersecurity mental models (authentication/MFA, encryption & key management, least privilege, OSINT/OPSEC, social engineering, integrity/hashing, availability/backups) without any on-screen computers. It is written for collaborators, IRB review, and methods sections.

## 1. Theoretical grounding

The design draws on the research frontier for adaptive educational games:

- **Dynamic Difficulty Adjustment (DDA).** Adapting challenge to the learner improves engagement and learning; reviews recommend adjusting on *multiple* performance measures rather than a single signal (Seyderhelm & Blackmore; recent SLRs, 2024–2025).
- **Elo-based learner modeling.** A lightweight Elo rating updates ability and item difficulty online after each response; it is simple, fast, explainable, and competitive with IRT/Bayesian models for adaptive practice (Pelánek, 2016; dynamic-K extensions, 2025).
- **Evidence-Centered Design (ECD) + Stealth Assessment.** Assessment is embedded invisibly in gameplay and used to drive scaffolding/difficulty; grounded in Vygotsky's **Zone of Proximal Development (ZPD)** — keep the learner challenged but not frustrated (Shute; Mislevy ECD).
- **Flow** (Csikszentmihalyi): the affective target the ZPD band operationalizes (challenge ≈ skill).

## 2. ECD architecture (how it maps onto the game)

| ECD element | Cipherfell realization |
|---|---|
| **Competency model** | The seven security mental models (one per act); measured by the pre/post knowledge check. |
| **Evidence model** | In-game telemetry: clean-solve (no hints, no missteps), hints used (manual + auto), missteps, time, and the Elo ability estimates derived from them. |
| **Task model** | Each puzzle is parameterized into **four difficulty tiers** (Novice / Apprentice / Journeyman / Master) with a per-play **seed** that varies the specific instance (cipher text & shift, keyring grid size, OSINT options, summons lines, ledger figures & tampered page). |

## 3. Adaptive engine

- **Ability.** A global ability `θ_G` and seven per-concept abilities `θ_c` (logit scale), persisted in `localStorage` (`cf_thetaG`, `cf_theta`) so returning learners are met at their level (act 1 adapts from history; a new learner starts at Novice/Apprentice and ramps up).
- **Update (Elo).** After each puzzle, `θ ← θ + K·(outcome − P)` with `K = 0.7`, where `P = σ(θ − δ_tier)` and **outcome is the binary clean-solve** (no hints, no missteps). The binary signal is essential: a continuous "partial credit" outcome makes `E[outcome] ≠ P`, which inflates `θ` and lets difficulty drift; the binary signal yields `E[outcome] = P(success)`, so `θ` converges (verified by simulation, §5).
- **Tier selection (ZPD).** The next act's tier is the one whose predicted success probability is nearest the ZPD target (`ZPD_OFF = 1.0`, i.e. P ≈ 0.7). Tier difficulties: `δ = [−1.5, −0.5, 0.5, 1.5]`.
- **Calibration.** Each solved item logs its predicted P (from entry `θ`+tier) and whether it was a clean solve; the session export reports mean predicted P vs. actual clean-solve rate vs. the ZPD target, so the model can be validated empirically across participants.

## 4. Layered learning support (scaffolding)

1. **Graduated hints** — three escalating hints per puzzle (nudge → strategy → near-answer), bilingual.
2. **Proactive scaffolding (stealth-driven)** — on an ~18 s stall the hint pulses; after a second misstep the next hint auto-surfaces (silently, not penalized) — support arrives when struggle is detected.
3. **Diagnostic feedback** — wrong answers get specific feedback (e.g., the exact role→door errors in the keyring; option-specific OSINT misconceptions).
4. **Worked examples** — shown only at the Novice tier (fading scaffolding).
5. **Optional AI tutor** — keyless Cloudflare Workers AI (English/Korean) gives concept-aware formative nudges that never reveal the answer; degrades to scripted hints when unavailable.
6. **Mastery profile** — the epilogue shows per-concept ability (θ → %) and flags the weakest competency.

## 5. Calibration evidence (Monte-Carlo)

A 4,000-learner simulation across ability cohorts (and replays) was used to validate the engine:

- The **binary** outcome removes θ drift (|θ̂ − θ| stays ~0.5 across replays vs. diverging to >1.1 with a continuous outcome).
- With four tiers, achieved clean-solve P sits in a healthy ZPD band — roughly **weak ≈ 0.57, average ≈ 0.70, strong ≈ 0.78** — i.e., the four-tier range lifts weak learners off the floor and centers the average on the target.

Re-run with `research/analyze_sessions.py` on real exports to check the model holds with participants.

## 6. Measurement & data

- **Consent gate** (anonymous; optional study ID). The game plays identically if declined; only consented sessions are logged.
- **Pre/post knowledge check** — seven transfer items, one per concept, options shuffled per administration; no feedback on pre (clean baseline), misconception feedback on post.
- **Telemetry** — timestamped events: consent, pre/post answers, clue pickups, seals, hints (manual `hint`, auto `hint_auto`, offered `hint_offer`), AI-tutor calls, adaptive updates (`adapt`), win.
- **CSV export** (client-side, one click) — sections: `# session` (ids, pre/post scores & delta, seals/hints/wrong/time/rating, seed, per-act tiers, θ_G, per-concept θ, calibration: `mean_predP`, `clean_solve_rate`, `zpd_target`), `# pre_answers`, `# post_answers`, `# events`.

### Suggested analyses
- Pre→post gain (paired *t*, Cohen's *d*); per-item and per-concept gains.
- Learning-curve: θ trajectory across acts/replays.
- Calibration: mean predicted P vs. actual clean-solve rate vs. 0.7 target.
- Support use vs. outcome (hints/auto-hints, AI-tutor) as covariates.

## 7. Limitations
- Single-play within-game adaptation spans only seven items; cross-play persistence is where adaptation compounds.
- Tier difficulties are author-set anchors, not empirically calibrated item parameters — the calibration export is the path to data-driven re-anchoring.
- Korean localization currently covers comprehension-/research-critical surfaces; some in-world dialogue falls back to English.

## References (frontier, indicative)
- Pelánek, R. (2016). *Applications of the Elo rating system in adaptive educational systems / Elo-based learner modeling.* UMUAI.
- Shute, V. J. et al. *Stealth assessment* and *Assessment and adaptation in games.* (ECD + ZPD).
- Seyderhelm & Blackmore. *Systematic review of dynamic difficulty adaptation for serious games.*
- Csikszentmihalyi, M. *Flow.* Vygotsky, L. *Zone of Proximal Development.*
