# Cipherfell — research kit

- **ADAPTIVE_DESIGN.md** — adaptive-learning & assessment design (ECD mapping, Elo/ZPD engine, scaffolding, measurement, CSV schema, cited frontier). For collaborators / IRB / methods sections.
- **analyze_sessions.py** — aggregate a folder of in-game CSV exports into a study summary *and* empirically re-anchor the difficulty model.
- **simulate_calibration.py** — generate synthetic exports from a known-truth model to validate the re-anchoring before real data exists.

## Study summary + re-anchoring

```bash
python analyze_sessions.py <folder-of-exported-csvs> --charts --out summary.csv
```
Reports pre/post gain (paired *t*, Cohen's *dz*), per-item & per-concept results, per-concept ability θ, support use, and — from the per-item `adapt` event log — a **calibration block**:

- **Per-tier placement health.** Each tier's achieved clean-solve rate (with a Wilson 95% CI) vs. the design target `P = sigmoid(ZPD_OFF) ≈ 0.73`, plus a first-order suggested anchor. *Caveat:* because the game **adaptively selects** which tier a learner sees, changing a tier's difficulty also changes who lands there, and Elo absorbs difficulty error into the ability estimate — so the per-tier suggestion is one iteration, not a one-shot solver. Re-collect after redeploying; the pre/post knowledge check is the external ability anchor.
- **Per-concept difficulty.** Each concept's observed clean-solve minus the game's own predicted P, **centered** by the grand-mean residual (which strips the global shift that within-session learning adds to every concept). Concept is orthogonal to the tier-selection variable, so this cleanly flags content that runs harder/easier than its siblings. Items flagged `<-- review items` are the ones to re-author.

Pass `--no-recalibrate` to skip the calibration block.

Each CSV is one participant's export (in-game ⚙ Settings → Export my data, available when research logging is on). Re-anchoring needs the `# events` section, which carries the per-item `adapt` rows (`c`, `tier`, `clean`, `pPred`).

## Validate the loop before you have participants

```bash
python simulate_calibration.py --out sim_data --learners 600 --plays 2
python analyze_sessions.py sim_data
```
The simulator mirrors the in-game adaptive loop exactly and plants a known ground truth (one tier harder than its authored anchor; concept `osint` harder and `auth` easier). Running the analyzer on the synthetic folder should:

- flag `osint` as the hardest concept (suggested `b_c` ≈ +0.5, planted +0.6) and `auth` as easier — i.e. the per-concept diagnostic recovers the planted ranking;
- show the under-target tier in the placement table.

To see the adaptive-selection coupling first-hand, feed a suggested anchor back as the game's operating tiers and re-measure:
```bash
python simulate_calibration.py --out sim2 --tiers="-1.20,-0.20,0.41,1.70"
python analyze_sessions.py sim2
```
This demonstrates why tier re-anchoring is iterative (and why the tool reports it as a suggestion, not a guarantee).
