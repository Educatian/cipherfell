# Cipherfell — Evidence Map (construct → evidence → mechanic → signal)

An audit of the game against the `game-evidence` method: every act's mechanic must
trace to a real, *verified* citation (no hallucinated refs) and be instrumented by a
telemetry signal. Citations below were checked live against the OpenAlex API
(titles, years, and DOIs resolve); cite counts are OpenAlex's as of 2026-06.

## Cross-cutting foundations (engine + framing)

| Construct | Verified evidence | Realized as |
|---|---|---|
| Stealth assessment (assess inside play, not a bolted-on quiz) | Shute, Ke & Wang (2013) *Stealth Assessment*, MIT Press — doi:10.7551/mitpress/9589.001.0001 (277); Arnab et al. (2014) *Mapping learning and game mechanics*, BJET — doi:10.1111/bjet.12113 (820) | Each puzzle is the assessment; the binary clean-solve drives the model |
| Elo learner modeling + DDA in the ZPD | Pelánek (2016) *Applications of the Elo rating system in adaptive educational systems*, Computers & Education — doi:10.1016/j.compedu.2016.03.017 (166); Zohaib (2018) *Dynamic Difficulty Adjustment: A Review* — doi:10.1155/2018/5681652 (204) | Per-concept + global Elo, 4 ZPD tiers (`ADAPTIVE_DESIGN.md`) |
| Challenge↔skill drives engagement & learning | Hamari et al. (2015) *Challenging games help students learn*, Computers in Human Behavior — doi:10.1016/j.chb.2015.07.045 (1639) | ZPD target P≈0.73; proactive scaffolding |
| Serious games are suitable for cyber training | Hendrix et al. (2016) *Game Based Cyber Security Training*, Int. J. Serious Games — doi:10.17083/ijsg.v3i1.107 (158); Bellotti et al. (2013) *Assessment in and of Serious Games* — doi:10.1155/2013/136864 (584) | The whole premise; pre/post KC bank |
| Users hold flawed security mental models | Adams & Sasse (1999) *Users are not the enemy*, CACM — doi:10.1145/322796.322806 (1387) | Distractors encode real misconceptions |

## Per-act audit

| Act / construct | Verified evidence | Mechanic requires the construct? | Telemetry signal | Verdict |
|---|---|---|---|---|
| **1 · Authentication / MFA** — identity rests on independent factors (know/have/is) | Ometov et al. (2018) *Multi-Factor Authentication: A Survey*, Cryptography — doi:10.3390/cryptography2010001 (416); Bonneau et al. (2015) *Passwords and the evolution of imperfect authentication*, CACM — doi:10.1145/2699390 (248); Ur et al. (2016) *Do Users' Perceptions of Password Security Match Reality?* — doi:10.1145/2858036.2858546 (157) | **Yes** — must cross-examine all three factors; the impostor passes the stealable factors and fails the unforgeable one | `c_know`, `c_have`, `c_are` (three **separate** clue signals = factor-level evidence), `adapt(clean,tier,θ)` | **PASS (strongest signal)** |
| **2 · Encryption / key management** — secrecy lives in the key, not the method | *Principle-grounded* (Kerckhoffs's principle; key-handling). Foundational: Lampson (1992) *Authentication in distributed systems*, ACM TOCS — doi:10.1145/138873.138874 (610) | **Yes** — turn the cipher wheel to recover the shift; discover the key written with the message | `c_decoded`, `c_cipher`, `adapt` | **PARTIAL — evidence gap** (no empirical game-pedagogy citation; rests on classical principle) |
| **3 · Least privilege** — minimum access shrinks the blast radius | Saltzer (1974) *Protection and the control of information sharing in Multics*, CACM — doi:10.1145/361011.361067 (398); Smith (2012) *A contemporary look at Saltzer & Schroeder's 1975 design principles*, IEEE S&P — doi:10.1109/msp.2012.85 (44) | **Yes** — re-cut the keyring to per-role minimum, then deduce the culprit from a now-singular access set | `c_keys`, `c_oldkey`, `adapt` | **PASS** |
| **4 · OSINT / OPSEC** — public + public can equal private (aggregation) | de Montjoye et al. (2013) *Unique in the Crowd: the privacy bounds of human mobility*, Scientific Reports — doi:10.1038/srep01376 (1593) | **Yes** — combine several harmless public scraps into one precise raid window | `c_osint` (+ chapel/ledger fragments), `adapt` | **PASS** |
| **5 · Social engineering / phishing** — forged authority + urgency; verify out-of-band | Sheng et al. (2007) *Anti-Phishing Phil*, SOUPS — doi:10.1145/1280680.1280692 (506); Kumaraguru et al. (2010) *Teaching Johnny not to fall for phish*, ACM TOIT — doi:10.1145/1754393.1754396 (392) | **Yes** — identify the four pretext levers, then choose a trusted-channel verification | `c_pretext`, `c_verify`, `adapt` | **PASS** |
| **6 · Integrity / hashing** — make tampering *detectable* by recomputing a checksum | *Principle-grounded* (cryptographic hashing / MAC; tamper-evidence). No clean empirical teaching study surfaced | **Yes** — re-tally each page and find the seal that no longer matches its true sum | `c_ledger`, `c_integrity`, `adapt` | **PARTIAL — evidence gap** (textbook principle, weak empirical pedagogy base) |
| **7 · Availability / backups / ransomware** — redundant off-site copies; restore, don't pay | Razaulla et al. (2023) *The Age of Ransomware: A Survey*, IEEE Access — doi:10.1109/access.2023.3268535 (110); Kapoor et al. (2021) *Ransomware Detection, Avoidance, and Mitigation*, Sustainability — doi:10.3390/su14010008 (99) | **Yes** — back up every record off-site, then restore instead of paying the ransom | `c_records`, `c_backups`, `c_avail`, `adapt` | **PASS** |

## Findings

**Strengths.**
- Every act is a genuine interactive loop where *succeeding requires exercising the construct* — none is a quiz bolted onto a game (the pre/post KC bank is the separate, explicit measure). This is the core `game-evidence` bar, and all 7 clear it.
- Every construct is instrumented: per-act `clue` signals + the `adapt` stealth-assessment (clean-solve, tier, θ) + `seal` completion + scaffolding (`hint`/`hint_auto`/`hint_offer`) + transfer (`kc_pre`/`kc_post`). Construct → signal is complete.
- Act 1 is exemplary: it emits the three MFA factors as **separate** clue events (`c_know`/`c_have`/`c_are`), so the telemetry evidences the sub-construct, not just the outcome.

**Gaps to close (priority order).**
1. **Evidence base for Acts 2 (encryption) and 6 (integrity).** Both rest on classical/textbook principles (Kerckhoffs; cryptographic hashing) rather than an empirical game-pedagogy citation like Anti-Phishing Phil (Act 5) or Unique in the Crowd (Act 4). Action: either cite the canonical primary sources explicitly (Kerckhoffs 1883; a hashing/MAC standard) and frame them as principle-grounded, or find a CS-education study on teaching crypto/integrity and add it. Until then these two acts are honestly *principle-grounded, not evidence-grounded*.
2. **Sub-construct telemetry for Acts 4–6.** Act 1's factor-level signals are the model. Acts 5 and 6 emit only outcome-level clues. Action: log *which* pretext lever the player flagged (Act 5) and *which* page's checksum they recomputed (Act 6), and *which* scraps were combined (Act 4), for richer stealth assessment.
3. **Distractor → misconception traceability.** The KC distractors encode real misconceptions (grounded by Adams & Sasse 1999), but that mapping is implicit. Action: tag each distractor with the misconception it represents, so the post-test feedback and the analyzer can report misconception prevalence.

**Verdict: 5 / 7 acts evidence-grounded (PASS), 2 / 7 principle-grounded (PARTIAL).** All 7 mechanic↔construct alignments and all 7 construct↔signal instrumentations hold. No fabricated citations: every reference above resolved live on OpenAlex.
