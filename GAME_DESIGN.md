# CIPHERFELL — The Warden's Eye

A cozy medieval-village mystery RPG that teaches **cybersecurity mental models**
without a single computer on screen. No hoodies, no neon, no "matrix" text rain.
The player learns to *think* like a security practitioner — suspect, verify, model
threats, contain blast radius, notice aggregation — through village intrigue.

## Why this beats the sci-fi cliché
Security is not green text. Its core is a handful of transferable *mental models*:
- **Authentication** = "is this person really who they claim?"
- **Confidentiality / encryption** = "can I move a secret past a hostile reader?"
- **Threat modeling / least privilege** = "who can touch what, and how bad if they turn?"
- **Information leakage / OSINT** = "harmless scraps, combined, become a secret."

Set those in a 13th-century village and the player practices the *reasoning*, not the
jargon. The transfer to real security is the payoff revealed in the epilogue.

## Premise
You arrive in **Cipherfell** as its new **Warden of the Seal** — the village officer
who vouches for who-is-who and keeps the Duke's correspondence safe. Within a day,
four things go wrong at once, and they are connected. A stranger at the gate claims to
be the long-absent merchant. The Duke's sealed order arrives already opened. The
granary keys multiply. And the rival Baron of Thornmoor always seems to know the
village's plans a day early. Solve the four, and the single hand behind them is exposed.

## The town (single hand-painted top-down map, walkable zones)
- **Gatehouse** (north) — Quest 1 hub: the stranger, the gate ledger.
- **Market Square** (center) — spawn point, the herald, notice board (journal recap).
- **The Tankard** tavern (west) — Quest 4 hub: gossip fragments.
- **Chapel** (east) — bell schedule fragment; the Captain prays here.
- **Granary + Archive** (south) — Quest 3 hub: keys, the steward.
- **Smithy** (southwest) — the blacksmith: a verification witness for Quest 1, signet lore.
- **Warden's Study** (your home, center-south) — Quest 2 hub: cipher wheel, sealed letters; the journal/inventory.

## The four quests (each = one concept, one mechanic, one "aha")

### Q1 — The Impostor at the Gate  →  Authentication & social engineering
A man claims to be **Aldric**, the merchant gone three winters to the city.
The gate guard already half-believes him (he's friendly, confident, knows a few
names — classic pretexting). The player gathers **verification factors** and learns
that any *single* factor is weak:
- **Something he knows** — a passphrase the real Aldric and the tavernkeeper shared.
- **Something he has** — Aldric's signet (but seals can be forged — see the prop pair).
- **Something he is** — a scar / the blacksmith's first-hand recognition.
Mechanic: collect 3 factor-claims, cross-examine, and notice the impostor passes the
*stealable* factors (a name overheard, a copied signet) but fails the *unforgeable* one.
Aha: **identity is layered; attackers target the weakest single factor → use more than one.**

### Q2 — The Sealed Letter  →  Encryption & confidentiality
The Duke's order must reach the Captain, but the spy reads everything that crosses the
square. In the Warden's Study you find a **brass cipher wheel** (Caesar shift). The player:
1. Decodes an *intercepted* enemy message (learn the wheel).
2. Encodes the Duke's reply so only the Captain (who holds the matching wheel setting) can read it.
3. Discovers a note where someone wrote the **shift key on the same parchment** as the
   message — the teachable failure: *never ship the key with the ciphertext.*
Aha: **secrecy lives in the key, not the method; key handling is the whole game.**

### Q3 — The Keyring  →  Threat modeling & least privilege
Grain is vanishing. The steward proudly hands **everyone the master key** "to save
trips." The player rebuilds the keyring: assign each role the *minimum* keys for their
job (granary-hand gets granary only, scribe gets archive only...). Then a small
**threat-model deduction**: list assets → who can reach each → who had access to *both*
the granary *and* a motive. Over-broad keys made everyone a suspect; least privilege
shrinks the suspect set to one.
Aha: **don't hand out the master key; minimize access so a betrayal's blast radius is small — and so you can actually reason about who-could-have.**

### Q4 — Loose Lips  →  Information leakage & OSINT aggregation
No single villager leaked anything secret. But the Baron's man only needs to *aggregate*:
the tavern's "big shipment Thursday," the laundry list showing the Captain's away-days,
the merchant ledger's wagon count, the chapel bell that rings early when the granary's
full. Each scrap is harmless. The player **collects 4 innocuous fragments** and combines
them on the notice board to reconstruct exactly what the Baron now knows — then plugs the
aggregation, not the people.
Aha: **public + public + public can equal secret; defend the aggregate, practice OPSEC.**

### Capstone — The Warden's Eye
The four threads converge: the spy used a **forged identity** (Q1) to get inside, read a
**poorly-keyed letter** (Q2), exploited the **master key** (Q3) to move unseen, and
**aggregated gossip** (Q4) to time it all. The player names the culprit by selecting the
one suspect consistent with all four constraints. Epilogue maps each village lesson to its
real security name (authentication / MFA, encryption & key management, least privilege &
threat modeling, OSINT & OPSEC).

## Systems
- Top-down movement on a painted map; walkable polygons + building door triggers.
- Input: keyboard (physical codes WASD/arrows), touch d-pad, gamepad.
- Dialogue: portrait + name + branching choices; choices feed quest state.
- **Journal/Clues**: every gathered factor/fragment is an item; puzzles read the journal.
- Quest state machine; capstone unlocks when all four resolve.
- All player-facing strings external (STRINGS object) for easy localization.

## STYLE FORMULA (byte-identical suffix appended to EVERY asset prompt)
> cozy hand-painted storybook illustration, medieval European village, warm muted
> earthy palette of parchment cream moss green terracotta and dusk-blue shadow, soft
> golden-hour lighting, rounded readable shapes, gentle dark outline, clean flat plain
> background, no text, no letters, no numbers, no watermark, no signature

## Asset manifest → see assets.csv
