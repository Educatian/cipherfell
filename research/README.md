# Cipherfell — research kit

- **ADAPTIVE_DESIGN.md** — adaptive-learning & assessment design (ECD mapping, Elo/ZPD engine, scaffolding, measurement, CSV schema, cited frontier). For collaborators / IRB / methods sections.
- **analyze_sessions.py** — aggregate a folder of in-game CSV exports into a study summary (pre/post gain with paired t & Cohen's dz, per-item & per-concept results, per-concept ability θ, difficulty calibration, support use). Stdlib-only stats; optional charts.

```bash
python analyze_sessions.py <folder-of-exported-csvs> --charts --out summary.csv
```
Each CSV is one participant's export (in-game ⚙ Settings → Export my data, available when research logging is on).
