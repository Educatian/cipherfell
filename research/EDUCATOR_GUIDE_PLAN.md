# Cipherfell — Educator Guide: research scan + development plan

A plan for an educator professional-development (PD) guide so K-12 and higher-ed
instructors can teach with **Cipherfell**. Grounded in a scan of existing AI-/digital-
literacy PD kits and the serious-game facilitation literature (sources at the end).
Cipherfell teaches cybersecurity mental models; this plan also bridges those to
**AI literacy** (AI-enabled phishing, scraping/inference, deepfakes, biometric spoofing),
so the guide sits inside the AI-literacy PD genre, not beside it.

## 1. What existing K-12 + higher-ed AI-literacy PD kits look like

| Kit | Audience | What it ships | Structural convention worth copying |
|---|---|---|---|
| **AI4K12** (AAAI + CSTA) | K-12 | "Five Big Ideas" framework, grade-banded guidelines, curated resource directory, activity guides, PD courses | A small **Big-Ideas spine** + grade bands + a **standards crosswalk**; resources hang off the framework, not vice-versa |
| **Experience AI** (Raspberry Pi Foundation + Google DeepMind) | K-12 (ages 11-14) | Lesson plans, **slide decks**, worksheets, videos, a free **3-week online teacher PD course** ("Understanding AI for educators"), partner-delivered training | A **teacher PD course separate from the lessons**; subject-agnostic so non-CS teachers can run it; "teacher-ready" packaged units |
| **Day of AI** (MIT RAISE) | K-12 (3-5, 6-8, 9-12) | Modular formats: **standalone lesson / 2-4-lesson sequence / 5-lesson unit / 6+ course**; everything on one page; PD + **train-the-trainer** | **Modular dosing** (one period up to a full unit) and one-page "everything you need"; train-the-trainer for scale |
| **UNESCO AI Competency Framework for Teachers (2024)** | global / both | 5 aspects × 3 progression levels (acquisition → deepening → creation) = **15 competency blocks**; "human-centered" values | A **progression-level matrix** and explicit human-centered/ethics values column |
| **EDUCAUSE — AI Literacy in Teaching & Learning (ALTL, 2024)** | higher ed | Tailored definitions/competencies/outcomes for **students, faculty, and staff** across four areas: **Technical Understanding, Evaluative Skills, Practical Application, Ethical Considerations** | The four-area competency split + **role-tailored** outcomes (student vs. faculty) |
| **Every Learner Everywhere — Faculty Development & GenAI Playbook** | higher ed / CTL | Strategies for Centers for Teaching & Learning to design GenAI faculty programming | A **CTL-facing facilitation playbook** (how to *run the PD*, not just the content) |
| **Barnard College AI literacy** | higher ed | Faculty workshops (GenAI 101), slide deck, open labs, syllabus-statement workshops | Low-stakes **open-lab + workshop** format; reusable slide deck |

**Serious-game facilitation literature** (distinct from AI-literacy kits, equally load-bearing):
- The learning lives in a **three-phase loop: pre-brief → play → debrief**, and *debriefing is "the processing of the game experience to turn it into learning"* (Springer DBR study; JMIR facilitator-competency study). A guide that only explains the game and skips structured debrief leaves the learning on the table.
- **Facilitator competencies and a "teacher console"** (observing/capturing gameplay data) materially change learning transfer. Cipherfell already has the console equivalent: its **CSV telemetry export** (per-act adaptive signals + pre/post KC).

### Conventions to adopt
1. A **small framework spine** (Cipherfell's seven mental models) + **standards crosswalk** (already drafted in `README.md`).
2. **Modular dosing** — single act (one period) → 7-act unit → semester module.
3. A **teacher PD layer separate from the student-facing lessons** (facilitator background so non-security teachers can run it).
4. The **pre-brief → play → debrief** loop per act, with the debrief as the core learning moment.
5. **Role-/level-tailored tracks** (K-12 middle/high vs. higher-ed) like EDUCAUSE's role split.
6. An **ethics / human-centered column** (UNESCO) — here, the AI-literacy bridge + responsible-disclosure norms.
7. **Data-informed teaching**: use Cipherfell's export + analyzer as the "teacher console."

## 2. Cipherfell assets the guide can build on (already in this repo)

- **7 acts** = seven mental models (auth/MFA, encryption, least privilege, OSINT, social engineering, integrity, availability) — the framework spine.
- **`README.md` curriculum crosswalk** — CSEC2017, NIST CSF 2.0, NICE, CISSP, CompTIA Security+, CSTA, AP CSP, CYBER.ORG. (Add AI4K12, ISTE, UNESCO, EDUCAUSE for the AI-literacy framing.)
- **`research/EVIDENCE_MAP.md`** — construct → evidence → mechanic → signal per act (the facilitator's "why this teaches what it claims").
- **`research/ADAPTIVE_DESIGN.md`** — the adaptive engine + measurement, for IRB/methods and for explaining the difficulty tiers to teachers.
- **Telemetry CSV export + `analyze_sessions.py`** — the teacher-console/data layer (pre/post gain, per-concept mastery, calibration).
- **Pre/post KC bank (21 items, parallel forms)** — built-in formative assessment.
- **Bilingual (EN/KO)** + **keyless AI tutor** + **accessibility pass** — equity affordances to foreground.

## 3. Proposed guide structure (section-by-section)

A single guide with a shared core and two tracks (K-12 / higher-ed), mirroring the conventions above.

**Front matter**
0. One-page "Start here" (what Cipherfell is, no install, the URL, ~time per act).

**Part A — Orientation (the PD layer)**
1. Why this matters: cybersecurity *as* AI literacy (the bridge table, §4).
2. The seven mental models in plain language (facilitator background; non-experts can run it).
3. Standards alignment crosswalk (security frameworks + AI4K12 BI-5, CSTA, ISTE, UNESCO AICFT, EDUCAUSE ALTL).
4. How the adaptive engine + tiers work, and what *not* to over-coach (let the ZPD do its job).

**Part B — Teaching with it (per-act lesson cards)**
For each act, a 1-2 page card: **pre-brief** (hook + the question) → **play** (what the student does, ~time, the misconception the distractors target) → **debrief** (3-5 discussion prompts + the real-world transfer, incl. the AI-risk scenario) → **check** (what the KC item probes) → **extend** (a homework/transfer task).

**Part C — Dosing & sequencing**
- Single act (one 45-50 min period), the 7-act unit (a week/two), or a semester module with the research instrument on.
- K-12 (middle/high) vs. higher-ed pacing, grouping, and depth notes.

**Part D — Assessment & data**
- Turning on consent + pre/post; reading the CSV with `analyze_sessions.py`; interpreting mastery profile and calibration; using telemetry for formative grouping. Privacy/FERPA-friendly framing (anonymous, local-by-default).

**Part E — Equity, accessibility, and responsible use**
- Bilingual use, the AI tutor, accessibility features; norms for teaching offensive techniques defensively (responsible disclosure); the human-centered/ethics column.

**Back matter**
- FAQ/troubleshooting, a printable one-page quick-reference, facilitator slide deck pointer, and the evidence base (`EVIDENCE_MAP.md`).

## 4. The AI-literacy bridge (per act) — to be drafted into Part A/B

| Act (security model) | Contemporary AI-risk framing | AI-literacy anchor |
|---|---|---|
| 1 Authentication/MFA | AI voice/face spoofing of biometric factors | AI4K12 BI-1 Perception; BI-5 Societal Impact |
| 2 Encryption/keys | who can read AI-pipeline data; model/secret leakage | EDUCAUSE Ethical Considerations |
| 3 Least privilege | scoping AI agents'/tools' access (over-permissioned agents) | UNESCO human-centered (agency) |
| 4 OSINT/OPSEC | AI scraping + inference / re-identification from public data | AI4K12 BI-5; data ethics |
| 5 Social engineering | AI-generated phishing, voice clones, deepfake pretexts | AI4K12 BI-5; Evaluative Skills |
| 6 Integrity/hashing | detecting tampered/deepfaked media; model/output integrity | Evaluative Skills |
| 7 Availability/backups | resilience against AI-accelerated ransomware | Societal Impact |

(Each bridge claim should be backed by a verified citation before publication, per the `game-evidence` guardrail.)

## 5. Development plan (phases & deliverables)

- **Phase 0 — Decisions (needs user input):** primary audience weighting (K-12 vs HE), format (printable PDF vs. in-repo web page vs. both), length target (lean 8-page quick-start vs. full ~25-page kit), and whether to commission a facilitator slide deck (Higgsfield/Codex) and short PD video.
- **Phase 1 — Source & verify:** finalize the standards crosswalk additions (AI4K12/ISTE/UNESCO/EDUCAUSE) and the AI-bridge citations (OpenAlex-verified, no hallucinated refs).
- **Phase 2 — Draft Parts A-C:** orientation + the seven per-act lesson cards + dosing. Reuse `EVIDENCE_MAP.md` and the README crosswalk.
- **Phase 3 — Draft Parts D-E:** assessment/data walkthrough (with a worked `analyze_sessions.py` example on the simulated cohort) + equity/responsible-use.
- **Phase 4 — Package:** `docs/EDUCATOR_GUIDE.md` (+ printable export), a one-page quick-reference, and an optional slide deck; link from `README.md` and the live site.
- **Phase 5 — Validate:** a teacher-facing read-through pass (clarity for non-experts), and align with the standards bodies' exact wording.

## 6. Open questions for the user
1. **Audience weighting** — lead with K-12 (middle/high) or higher-ed, or balanced two-track?
2. **Scope** — lean quick-start (~8 pp) first, or the full kit (~25 pp) in one pass?
3. **Format** — printable PDF, an in-repo/`docs/` web page, or both? (And do you want the facilitator slide deck + short PD video now or later?)
4. **Framing** — keep the AI-literacy bridge prominent (position Cipherfell as an AI-literacy tool), or keep it as one section and lead with cybersecurity?

## Sources (verified this session)
- AI4K12 — https://ai4k12.org/ ; Raspberry Pi Foundation overview — https://www.raspberrypi.org/blog/ai-education-ai4k12-big-ideas-ai-thinking/
- Experience AI — https://experience-ai.org/en/ ; PD course context — https://www.raspberrypi.org/blog/experience-ai-deepmind-ai-education/
- Day of AI (MIT RAISE) — https://dayofai.org/curriculum-resources ; https://raise.mit.edu/
- UNESCO AI Competency Framework for Teachers (2024) — https://www.unesco.org/en/articles/ai-competency-framework-teachers
- EDUCAUSE — AI Literacy in Teaching & Learning (2024) — https://www.educause.edu/content/2024/ai-literacy-in-teaching-and-learning/faculty-altl
- Every Learner Everywhere — Faculty Development & GenAI Playbook — https://www.everylearnereverywhere.org/resources/faculty-development-and-gen-ai-playbook/
- Barnard College — Generative AI / AI literacy — https://barnard.edu/generative-ai
- Serious-game facilitation (DBR) — https://telrp.springeropen.com/articles/10.1186/s41039-017-0056-6 ; facilitator competencies — https://games.jmir.org/2021/2/e25481 ; educator's guide to serious games (med ed) — https://pmc.ncbi.nlm.nih.gov/articles/PMC9399447/
