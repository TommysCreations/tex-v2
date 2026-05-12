# Film 04 — Ground Truth (Answer Key)

**Scouted team:** Montverde Academy · **Opponent:** Brewster Academy (Boys' National) · **Event:** Nike EYBL Scholastic League (2025-26 season)
**Prompt 0B output shape:** this document mirrors the synthesis structure so TEX's output
can be graded section-by-section against what's here.

This is the authoritative answer key for grading TEX against film 04. Synthesized from
`film_watch_notes.md`. The numbers, names, and tendencies below are the ground truth;
TEX's `chunk_synthesis` output is graded line-by-line against this.

> **Rule 1:** every claim attributes to a jersey number + name.
> **Rule 2:** every count is a number, not a range, unless you explicitly flag uncertainty.
> **Rule 3:** every claim has a confidence tag: `[CONFIRMED]` / `[LIKELY]` / `[SINGLE GAME SIGNAL]`.
>   - `[CONFIRMED]` — observed 3+ times across multiple chunks, or 8+ occurrences total
>   - `[LIKELY]` — observed 2 times, or 4–7 occurrences total
>   - `[SINGLE GAME SIGNAL]` — observed once or only in one chunk. Possible tendency. Not confirmed.
> **Rule 4:** if you don't know, write "insufficient observation" — do not guess.

**Context note:** This is high-school prep program play (EYBL Scholastic), same league as
Film 03 (Spire / La Lumiere). Montverde Academy is one of the most well-coached prep
programs in the country — expect structured half-court offense with named sets. The watch
notes confirm this: multiple named structures (Horns, 1-4 flat, 4-out 1-in, BLOB sets)
appear repeatedly across chunks. Unlike Films 01–02 (AAU iso-default), Montverde runs
real structure. Don't force a "no set" finding.

---

## SECTION 1 — GAME HEADER

| Field | Value |
|---|---|
| Scouted team | Montverde Academy |
| Opponent | Brewster Academy (Boys' National) |
| Final score | Montverde `76` — Brewster `71` (margin +5, Montverde win, close late) |
| Winner | Montverde Academy |
| Game format | Four 8-min quarters, EYBL Scholastic / HS prep (32 min regulation) |
| Total offensive possessions by Montverde | `67 logged` (chunk totals: 18 / 16 / 22 / 11). High confidence — all four chunk possession tables are dense and complete. Per watch-notes whole-game wrap-up. |
| Total offensive possessions by opponent | Insufficient observation — Brewster possessions were not logged 1-for-1; only noteworthy defensive events and ball-screen coverages were tracked. Rough parity inferable from score / pace (~65–70) but not traceable to the scratchpad. |
| Score progression | 0–0 (start) → Montverde 19–17 (Q1 1:01) → Montverde 24–17 (end Q1) → Montverde 28–20 (end of chunk 0, mid-Q2) → Montverde 44–28 (halftime) → Montverde 49–28 (Q3 7:22, end of chunk 1) → Montverde 58–49 (end Q3) → Montverde 63–61 (Q4 5:00) → Montverde 66–64 (end of chunk 2, Q4 3:55) → Montverde 68–69 (Q4 2:47, **Brewster takes the lead briefly**) → Montverde 72–71 (Q4 2:00, +1) → Montverde 76–71 (final) |
| Game shape | Montverde controlled the first half (up 44–28 at the break, a +16 lead). Brewster mounted a comeback starting late in Q3 — closing the gap to 9 at the end of Q3 (58–49), then erasing the lead entirely in Q4 to briefly take the lead 68–69 at Q4 2:47. Montverde retook the lead and survived at the free-throw line for the win. **Game WAS close late** — margin at Q4 2:00 was 1 point. Final 2:00 included Brewster's intentional-foul-to-extend sequence over the final ~14 seconds. |
| Date of game | 2025-26 EYBL Scholastic season (exact date not captured in metadata) |
| Event | Nike EYBL Scholastic League — 2025-26 season |
| Source film | YouTube `tBnjFA64RSc` (film_id TBD post-upload) |

---

## SECTION 2 — OFFENSE: SET AND ACTION INVENTORY

**Framing note:** Montverde runs a structured half-court offense with multiple named
actions. The dominant half-court look across all four chunks is **1-4 flat / high
PnR** centered on `#3 Tyndale` + `#42 Daniels`. Horns is the second-most-frequent
named action and the primary diet of chunks 0–1. A 4-out 1-in / motion / 5-out
family is the early-game look (heavy in chunk 0) that gradually gives way to PnR-
centric possessions as the game progresses. **This is a real finding about
Montverde — they have genuine half-court structure, materially different from
Films 01 / 02 and consistent with Film 03's well-coached prep-program pattern.**

*Counts reconcile scratchpad language per §10a. Sorted by total occurrences descending.*

### Action A: 1-4 flat / High PnR (#3 + #42, with #2 / #11 secondary handlers)

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~17` (breakdown: chunk 0: `1` (poss 6), chunk 1: `4` (poss 6, 7, 9, 12), chunk 2: `9` (poss 2, 8, 10, 12, 13, 14, 16, 21, 22), chunk 3: `3` (poss 3, 5, 8)).
  - Representative possessions: C0-6 (`Q1 4:52` high PnR → #3 drives + stops in paint → bad pass `[TO]`), C1-6 (`Q2 4:32` 1-4 flat — #3 has ball top, two ball screens, attacks + draws foul), C1-12 (`Q2 1:13` 1-4 flat high PnR — #3 goes opposite of screen + lobs to #10 `[2pt make]`), C2-8 (`Q3 4:00` 1-4 flat — Montverde attacks Brewster's drop coverage, #3 small + fast `[2pt make]`), C2-14 (`Q4 0:23` 1-4 flat double high PnR — #3 sets right ball screen + pops, OREB sequence → `[2pt make]`), C2-21 (`Q4 4:51` high PnR — #2 comes off, kicks to #1 corner `[3pt make]`), C3-3 (`Q4 2:42` high PnR — #2 drives + draws foul `[FT 2-of-2]`), C3-5 (`Q4 1:54` high PnR — drive-kicks then reset, ref stops play for #1 cramping).
- **Primary initiator(s):** `#3 Tyndale` (primary PnR ball-handler — ~10 of ~17). `#2 Miller` (secondary handler — ~4 of ~17 including the C2-21 3pt-make sequence and C3-3 + C3-8 late-game PnR). `#11 Delancy` (~2 — C1-9, C2-1-adjacent rim drives).
- **Primary screener(s):** `#42 Daniels` (primary screener — ~12 of ~17 PnRs explicitly list #42 as screener). `#10 Koulisianis` (when subbed in — C1-7, C1-12 lob recipient as roller).
- **Typical floor position:** 1-4 flat alignment (handler top, four off-ball spaced flat). Primary action is top-of-key high PnR with #42. Spacing pulls Brewster bigs out — Montverde then attacks drop coverage or kicks to perimeter shooters.
- **Success rate:** `~8 of ~17 produced points or FT trips` (C1-12 lob 2pt make, C1-6 FT, C2-8 2pt make, C2-10 FT, C2-14 OREB→2pt make, C2-20 FT, C2-21 3pt make, C3-3 FT, C3-4 FT). Roughly 50% conversion — Montverde's reliable bucket-getter when motion stalls.
- **Key counter (if taken away):** Reset into Horns (Action B) or drop-back into 4-out 1-in motion (Action C). Late-game (chunk 3), the PnR converts to drive-and-finish or FT-drawing rather than kick-out 3s — Brewster pressured the ball more in Q4.
- **Reconciliation note:** Per §10a, unified "1-4 flat," "1-4 flat high PnR," "1-4 flat double high PnR," "high PnR," "PnR" (when initiated from flat alignment), and `"1-4 floor"` (C2-16, scratchpad typo) under this category. The handle / screener combination varies (#3+#42 dominant; #2+#42, #11+#10 secondary) but the structural action is identical.
- **Situational use:** Increases steadily across the game — 1 in chunk 0, peaks at 9 in chunk 2 (Brewster's comeback chunk), 3 in chunk 3 (late-game). Becomes Montverde's primary late-game half-court action.

### Action B: Horns / Horns-DHO (#3 + #42 / #1 at elbows)

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~10` (breakdown: chunk 0: `5` (poss 5, 12, 16, 17, 18), chunk 1: `2` (poss 2, 16), chunk 2: `2` (poss 7, 20), chunk 3: `1` (poss 4)).
  - Representative possessions: C0-5 (`Q1 5:34` horns — #3 comes off left-side screen + hits `[3pt make]` no passing), C0-12 (`Q1 1:46` horns — #3 drives + kicks `[3pt make]`), C0-17 (`Q2 6:50` horns — #3 gives up ball, gets it back in DHO, forces back-door pass `[TO]`), C0-18 (`Q2 6:33` horns / DHO — full action DHO with #42 and #11 → #11 drives + kicks `[3pt make]`), C1-2 (`Q2 5:48` horns — left-horn cross-top using right horn as screen, right horn pops, left horn screens down, then PnR drive-pull-up `[2pt make]`), C2-7 (`Q3 4:30` Horns — #3 uses screen, drives + kicks `[3pt miss]`), C2-20 (`Q4 5:35` horns — #3 high PnR with #42, hits roller `[FT 1-of-2]`), C3-4 (`Q4 2:14` horns — #11 comes off right screen + pulls up, gets fouled `[FT 2-of-2]`).
- **Primary initiator(s):** `#3 Tyndale` (primary — ~7 of ~10). `#11 Delancy` (~2 — C1-2 as flow-receiver, C3-4 as foul-drawer). `#42 Daniels` (C0-18 as DHO initiator).
- **Primary screener(s) / elbow players:** `#42 Daniels` (most common elbow). `#1 Philon` (paired-elbow). `#11 Delancy` (occasional flow-screener at elbow on C1-2's screen-the-screener sequence).
- **Typical floor position:** Two bigs / forwards at the elbows (canonical Horns alignment). Initiator uses elbow screen, then flows into DHO with the other elbow or rejects + drives. Common counter: handler curls baseline-side off the elbow then kicks for a perimeter 3.
- **Success rate:** `~6 of ~10 produced points or FT trips` (C0-5 3pt, C0-12 3pt, C0-18 3pt, C1-2 2pt, C2-20 FT, C3-4 FT). High-efficiency action — Montverde's most reliable 3pt-generator.
- **Key counter (if taken away):** Reset into 1-4 flat / High PnR (Action A) or flow into open-floor drive-and-kick from a wing receiver.
- **Reconciliation note:** Unified "horns," "horns / DHO," "horns/DHO," and "Low horns" (C1-16 — same set with slightly lower elbow positioning, post-halftime) under this category. The DHO embedded inside Horns is structural, not a separate set.
- **Situational use:** Heavy in chunk 0 (5 occurrences — Montverde's opening half-court diet). Becomes less frequent as Brewster's defense adjusts (2 in chunk 1, 2 in chunk 2, 1 in chunk 3). Replaced by Action A as the late-game primary.

### Action C: 4-out 1-in / 5-out / motion (early-game diet)

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~14` (breakdown: chunk 0: `8` (poss 1, 2, 3, 7, 8, 9, 10, 11), chunk 1: `1` (poss 14), chunk 2: `3` (poss 1, 3, 19), chunk 3: `2` (poss 2, 7)).
  - Representative possessions: C0-1 (`Q1 8:00` 4-out 1-in — #2 refuses screen, drives + draws help, lobs to #42 `[2pt dunk]`), C0-2 (`Q1 7:16` motion — screen-the-screener sequence #42 down-screen → #3 screens for #1 at elbow → #1 curls + makes shot `[2pt make]`), C0-7 (`Q1 4:32` 4-out 1-in — ball swung around, #11 drives baseline `[2pt make]`), C0-9 (`Q1 3:19` motion — pass + cut in direction of pass, lots of action, #3 tough shot `[2pt make]`), C0-10 (`Q1 2:42` 4-down — Montverde all start baseline, pop to top, 2 passes + shot `[3pt miss]` — quick shot), C2-1 (`Q3 6:41` 4-out 1-in — 1 pass + drive `[FT 2-of-2]`), C2-19 (`Q4 6:13` 5-out — pass-and-cut-opposite, #11 left wing called for PnR with #42, #11 drives + open layup `[2pt make]`), C3-2 (`Q4 3:19` left-side overload — downscreen for #1 not used, #3 drives + kicks to #1 `[3pt miss]`), C3-7 (`Q4 0:54` 4-flat — #2 holds ball, Brewster pokes OOB).
- **Primary initiator(s):** `#3 Tyndale`, `#11 Delancy`, `#2 Miller`, `#1 Philon` — roughly evenly distributed. Not a single-initiator action like the PnR family.
- **Primary screener(s):** Varies — #42 Daniels (down-screens in C0-2, C0-8), #1 Philon (off-ball screens), #11 Delancy (screens for #1 at elbow C0-2). The action is structurally pass-and-cut with occasional embedded screens.
- **Typical floor position:** 4-out 1-in (four perimeter, one post) or 5-out (all five above the arc). Movement is pass-and-cut-opposite, ball-swing, occasional embedded screen-the-screener. Mid-possession a drive triggers a kick-out to a perimeter shooter or a dump to the post.
- **Success rate:** `~7 of ~14 produced points or FT trips` (C0-1 dunk, C0-2 2pt, C0-4 3pt make — but that's PnR/DHO embedded, C0-7 2pt, C0-9 2pt, C0-10 3pt miss, C2-1 FT, C2-19 2pt). Reasonable efficiency early, declines as Brewster's pressure increases.
- **Key counter (if taken away):** Late shot-clock fall-through into PnR (Action A) or Horns (Action B).
- **Reconciliation note:** Per §10a, unified "4 out 1 in," "5 out," "motion," "4 down," "left side overload," and "4 flat" (in non-BLOB contexts) under this category. These are spacing variants of the same continuity-flow offense. Some "motion" possessions (C0-2 with screen-the-screener) overlap structurally with Horns flow — flagged in §10a as a true ambiguous boundary.
- **Situational use:** **Heavily concentrated in chunk 0** (8 of 14 — Montverde's opening half-court diet before pivoting to PnR + Horns). Drops off sharply in chunks 1–2 as Brewster adjusts and Montverde commits to PnR-centric attack.

### Action D: Transition / push

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~9 opportunities / ~5 scores or FT trips` (breakdown: chunk 0: `2 opps / 1 score` (poss 14 `[2pt make]`, poss 15 `[TO]`), chunk 1: `5 opps / 3 scores` (poss 1 `[3pt miss]`, poss 4 `[2pt make]`, poss 5 `[3pt miss]`, poss 8 `[2pt make]`, poss 13 `[2pt make]`), chunk 2: `2 opps / 1 score-equivalent` (poss 11 `[FT 2-of-2]`, poss 15 `[2pt miss]`), chunk 3: `0 opps / 0 scores`).
  - Representative possessions: C0-14 (`Q1 0:42` transition — #1 dunk off great passing in transition `[2pt make]`), C1-4 (`Q2 5:04` transition — #11 steals + passes ahead to #3 `[2pt layup make]`), C1-8 (`Q2 3:51` transition — #3 long rebound, 2-on-1, ball poked + recovered + finished `[2pt make]`), C1-13 (`Q2 0:45` transition — #3 pushes from outlet, #42 runs floor `[2pt make]` — "very strong"), C2-11 (`Q3 2:04` transition — #3 pushes fast, great pass `[FT 2-of-2]`).
- **Primary initiator(s):** `#3 Tyndale` (primary push-handler — most explicit "pushes ball" notes attribute to #3). `#11 Delancy` (steals → push, C1-4 example). `#1 Philon`, `#2 Miller` (occasional rebound-and-go).
- **Success rate:** `~5 of ~9 produced points or FT trips` (~55% conversion). Slightly above coin-flip — transition is a real positive mode for Montverde.
- **Reconciliation note:** All "transition" rows consolidated. Mostly off steals (especially in chunk 1) or long rebounds (#3 the typical push-trigger).
- **Situational use:** **Heaviest in chunk 1** (5 of 9 — Montverde's fast-break game peaked when defense was forcing TOs and rebounds in Q2). Drops in chunk 2 and disappears entirely in chunk 3 (intentional-foul-driven possessions, no time for transition). The transition opportunities also reflect game state — Brewster's late comeback meant Montverde was inbounding after Brewster makes more often, killing transition triggers.

### Action E: Iso / late-clock 1-on-1

- **Confidence:** `[SINGLE GAME SIGNAL]`
- **Total occurrences:** `1` (chunk 3 poss 6).
  - C3-6 (`Q4 1:35` late-clock iso — 7 seconds left on shot clock at start of possession, #11 takes player 1-on-1 + scores tough shot `[2pt make]` — "#11 play maker too like #3").
- **Reconciliation note:** Iso is rare in this film. Unlike Films 01 / 02 (AAU iso-default), Montverde does not default to 1-on-1 creation. The single late-clock iso is real but isolated.
- **Situational use:** Pure late-clock / late-game situation. Not a base mode.

### Single-occurrence / variant actions (one-line each, listed for completeness)

*Not part of the repeating inventory but observed:*

- `C0-4 Q1 6:08` — Left-side PnR + right-side DHO combo — #2 ghost screen + ball swing → DHO → #11 baseline drive + kick back to #2 top-of-key `[3pt make]`. Hybrid of Actions A and B.
- `C0-13 Q1 1:01` — BLOB (stacked left, 1 on right). See §4.
- `C1-3 Q2 5:19` — Drive-and-kick — #1 gets pass from #11 `[3pt miss]`. Variant in the motion family.
- `C1-9 Q2 3:16` — 1-4 flat **against Brewster 1-2-2 zone** — 1 pass + shot, quick `[3pt miss]`. Reactive variant.
- `C1-10 Q2 2:50` — 2-2-1 offense **against Brewster 1-2-2 zone** — 1 player middle, 1 player center under basket, middle kick-out led to drive + foul `[FT 2-of-2]`. Reactive to Brewster zone.
- `C1-11 Q2 2:05` — Continuation of zone offense — #2 attacks middle of zone + dumps to #42 `[2pt dunk make]`. Reactive zone offense.
- `C2-6 Q3 5:07` — "2 on elbow, 2 in corner" — miscommunication on pass `[TO]`. Likely a designed inbound continuation.
- `C2-9 Q3 3:09` — 2 guards up against 1-2-2 zone — forced drives + `[TO]`. Reactive.

**Reminder on what's NOT here:** No Spain PnR. No Flex (in the named sense). No Iverson cut. No Princeton-entry sets. No designed elevator screens. The named inventory is **1-4 flat / High PnR + Horns + 4-out 1-in motion + transition + BLOB family + occasional iso**. TEX outputs that produce "Spain PnR," "Flex," or "Iverson" terminology from this film are hallucinating.

---

## SECTION 3 — OFFENSE: TEMPO AND PACE

- **Primary tempo:** `moderate halfcourt with structured entries` — Montverde plays patient half-court basketball in the first half (Horns / 4-out 1-in / motion), pushing in transition opportunistically when steals or long rebounds present themselves. Pace feel logged as **"Montverde in control most of the chunk — good defense, controlling the game"** for chunk 1 (per scratchpad). `[CONFIRMED]`
  - **Frequency evidence:** ~9 transition opportunities logged across 67 possessions (~13% transition rate). Comparable to Film 03 Spire (~9%) — both are well-coached prep programs with structured half-court diets.
  - Typical transition triggers: steals (C1-4, C1-8 trap-and-go), long rebounds (#3 pushes), outlet passes (C1-13 with #42 trailing).
- **Average time to half-court action initiation:** `moderate` (6–12s). Montverde enters into Horns or 1-4 flat on most half-court possessions. Initial pass to wing or elbow, then action develops over 3–6 seconds.
- **Pace changes (situational):**
  - **First half control / second half acceleration.** Chunks 0–1 (Q1–Q2) are deliberate half-court. Chunks 2–3 (Q3–Q4) accelerate as Brewster's comeback forces faster decisions and more transition off TOs. Per chunk 2 pace note: **"Toward the end of the chunk, Brewster makes their comeback and takes momentum — Montverde with too many T.O.s and losing too many 50/50 balls to Brewster. Brewster hitting big shots."** `[CONFIRMED]`
  - **Late-game pace dictated by intentional fouls.** Final ~14 seconds of chunk 3 (poss 9, 10, 11) are intentional-foul-driven — Brewster fouls right away, Montverde shoots FTs. Not normal possessions. `[CONFIRMED]`
  - **Chunk-3 wrap-up note:** **"Brewster carried their momentum from end of Chunk 2 into Chunk 3 — they had the momentum down the stretch. Montverde survives for the win."** Game shape is wire-to-wire Montverde control → Brewster comeback → Montverde survives. `[CONFIRMED]`
- **Confidence on tempo claims:** `[CONFIRMED]` overall. The "moderate halfcourt with structured entries" finding is well-supported across all 4 chunks; the transition rate is `[LIKELY]` because some live-tracked transition tallies were sparsely filled (chunk 1 BR-transition row left empty).

---

## SECTION 4 — OFFENSE: OUT-OF-BOUNDS SETS

*BLOB = baseline out-of-bounds. SLOB = sideline out-of-bounds.*

### BLOB #1: 4-flat baseline (4 players across baseline)

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `4` (`Q2 4:12` chunk 1 special, `Q3 5:27` chunk 2 poss 4 / special `Q3 5:26`, `Q4 7:01` chunk 2 poss 18 / special, `Q3 5:27` shares structure with `Q3 5:26` — same formation, two consecutive failed BLOBs).
  - `Q2 4:12` (chunk 1 special) — 4 flat across baseline. Lob to player on block who pops out a bit. `[2pt make]` (inbounded then scored on subsequent action).
  - `Q3 5:27` (chunk 2 poss 4) — BLOB 4-across. #1 on baseline pops to top elbow for inbound pass, drove ball. `[foul on floor]`.
  - `Q4 7:01` (chunk 2 poss 18) — BLOB 4-across. #1 pops to elbow for pass, dribbles over, feeds #42 in post `[2pt make]`.
- **Primary target (who's supposed to score):** `#1 Philon` (elbow popper / receiver — appears in 2 of 3 4-across BLOBs as the elbow popper). Designed first option is the elbow pop + safe inbound, then flow into half-court action.
- **Screeners:** Block / corner players (typically #42, #11, #3 depending on lineup). Not a screen-heavy alignment — primarily a popper-pop action.
- **Structural description:** 4 players across baseline (block / lane / lane / block), 1 inbounder under basket. First option is an elbow pop by a forward (#1) for the inbound; secondary option is a lob to the block-side big.
- **Success rate:** `2 of 3 inbounded successfully → score or foul drawn`. The Q4 7:01 → #42 post layup is the cleanest score off the set.
- **Reconciliation note:** This is Montverde's go-to BLOB formation — appears in 3 separate game segments.
- **Situational use:** Q2 4:12 was a midway-Q2 BLOB; Q3 5:27 and Q4 7:01 were in the comeback / lead-protect windows. Used regardless of game state.

### BLOB #2: Stacked left (3-stack on left, 1 on right)

- **Confidence:** `[SINGLE GAME SIGNAL]`
- **Total occurrences:** `1` (chunk 0 poss 13, `Q1 1:01`).
  - `Q1 1:01` — Stacked formation: 3 players stacked on left side, 1 on right. #1 got ball in paint and scored with foul `[and-1 → 2pt make + FT make]`. **The cleanest scoring BLOB in the film.**
- **Primary target:** `#1 Philon` (got ball in paint, scored + foul).
- **Reconciliation note:** Different formation from the 4-flat. Likely a designed scoring play — #1 was the explicit target, not just a safe inbound.
- **Situational use:** First-half BLOB after a Montverde stop. One of the highest-leverage scoring possessions in the chunk.

### BLOB #3: 3-across baseline + 1 halfcourt (alley-oop attempt)

- **Confidence:** `[SINGLE GAME SIGNAL]`
- **Total occurrences:** `1` (chunk 1 poss 15, `Q2 0:02`).
  - `Q2 0:02` — 3 players flat across baseline + 1 halfcourt. Play from far low-wing cuts to basket for an open alley-oop layup. `[2pt miss]`. End-of-half last-second look.
- **Primary target:** `#12 Ndour` (initiator and cutter — listed as the lob receiver per scratchpad).
- **Reconciliation note:** End-of-period designed alley-oop. Different from the 4-flat and stacked formations. Single-use last-second play.
- **Situational use:** End-of-half. Did not score.

### BLOB #4: Block / corner / elbow / top-of-key spread

- **Confidence:** `[LIKELY]`
- **Total occurrences:** `2` (chunk 2 poss 5 `Q3 5:24`, chunk 2 special `Q4 3:55` which flows into chunk 3 poss 1).
  - `Q3 5:24` (chunk 2 poss 5) — #11 block, #1 same-side corner, #42 elbow, #3 top-of-key. **Didn't set screen — just exchanged spots, couldn't get open.** `[TO]`. **Critical scouting flag** — Montverde failed to execute this BLOB.
  - `Q4 3:55` (chunk 2 special, flows into chunk 3 poss 1) — Block, middle paint, 1 player on elbow, outlet player deep top-of-key. **Cross-screen on 2 low players to get open** — flowed into #11's 2pt make at start of chunk 3.
- **Reconciliation note:** Similar spread alignment in both cases (block / corner / elbow / top variants). The cross-screen / exchange action is the key feature. Q3 5:24 failure was due to no screen being set — a real execution flag.
- **Situational use:** Mid-Q3 and start of close-late chunk 3. Used in higher-pressure situations than the 4-flat.

### SLOB sets

- **Total occurrences observed:** `1` (chunk 2 poss 17 / special, `Q4 7:11`).
  - `Q4 7:11` — SLOB box formation. Elbow screen-down to box, comes up for ball. Inbound succeeded but the follow-up was a bad pass kicked off Brewster's leg `[Montverde retains via OOB]`.
- **Confidence:** `[SINGLE GAME SIGNAL]`.
- **Reconciliation note:** Box-formation SLOB. Similar shape to Spire's Film 03 box-BLOB but used from the sideline here.

### ATO sets

- **Total occurrences observed:** `0` cleanly tagged as ATO in the scratchpad. Several BLOBs followed stoppages but were not explicitly tagged ATO.
- **Confidence:** `[NOT OBSERVED]`.

### Late-clock / end-of-period plays

- **C1-15 `Q2 0:02`** — End-of-half BLOB alley-oop attempt — see BLOB #3 above. Missed.
- **C3-6 `Q4 1:35`** — Late-clock iso, #11 1-on-1 score (see §2 Action E). `[SINGLE GAME SIGNAL]`.

*Noting: Montverde ran ONE clearly designed end-of-period set (the C1-15 alley-oop). Other late-clock possessions devolved into PnR or iso. `[LIKELY]` minimal end-of-period set inventory.*

---

## SECTION 5 — OFFENSE: LATE-GAME (final 8 minutes of close games)

- **Close late?** `YES` — at the 2:00 mark of Q4, Montverde led by **1** (72–71). Brewster briefly took the lead 68–69 at Q4 2:47. Final margin +5 with Montverde icing the game at the FT line. Game shape: **wire-to-wire control → Brewster comeback → Montverde survives.** This is real close-game data, not blowout protection.
- **Late-game tendencies — GAME CLOSE.** The chunk-3 possessions (Q4 3:55 → end) are the answer key for close-late execution.

### Chunk-3 final-stretch possession rundown (the actual late-game data)

*Personnel at start of chunk 3: `#3 #1 #2 #11 #42`. At Q4 1:33, #10 came in for #1 (cramping). Final-game personnel: `#3 #2 #11 #10 #42`.*

- **`Q4 3:55`** (poss 1) — Out-of-BLOB possession (BLOB #4 / block-corner-elbow-top spread). #11 made a tough well-guarded shot `[2pt make]`. **Score: 68–64 Montverde.**
- **`Q4 3:19`** (poss 2) — Left-side overload (4-out variant). Down-screen for #1 not used. #3 drives + kicks to #1 for an open `[3pt miss]`.
- **`Q4 2:42`** (poss 3) — High PnR (Action A). #2 drives to basket + draws foul → `[FT 2-of-2]`.
- **`Q4 2:14`** (poss 4) — Horns (Action B). #11 comes off right screen, pulls up for jump shot, gets fouled → `[FT 2-of-2]`.
- **`Q4 2:00`** (milestone, not a possession) — **Montverde 72 / Brewster 71 — margin +1**.
- **`Q4 1:54`** (poss 5) — High PnR (Action A). Drive-kicks, reset for high PnR, then ref stops play due to **#1 Philon cramping**. **Possession ends due to injury stoppage.**
  - **Personnel change at Q4 1:33:** #10 Koulisianis in for #1 Philon. Late-game closer lineup: `#3 #2 #11 #10 #42`.
- **`Q4 1:35`** (poss 6) — **Late-clock iso (Action E).** 7 seconds on shot clock at start of possession. #11 takes player 1-on-1 + makes a tough shot `[2pt make]`. **Scratchpad note: "#11 play maker too like #3."**
- **`Q4 0:54`** (poss 7) — 4-flat (Action C). #2 holds the ball. Ball poked out of bounds by Brewster — **Montverde retains** (OOB clock burn).
- **`Q4 0:39`** (poss 8) — High PnR (Action A). #2 goes 1-on-1 + `[TO]`. **Critical late-game turnover.**
- **`Q4 0:13`** (poss 9) — No designed action. #3 initiator. Brewster fouls immediately. `[foul on floor]`.
- **`Q4 0:10`** (poss 10) — No designed action. Brewster fouls immediately. `[FT 1-of-2]` (initiator listed as #1 — see §10c for attribution flag, since #1 had been subbed out at Q4 1:33). Result is a Brewster intentional-foul-to-extend sequence.
- **`Q4 0:04`** (poss 11) — No designed action. Brewster fouls immediately. `[FT (detail TBD — see §10b)]`.
- **Final score: Montverde 76, Brewster 71 (+5).**

### What IS observable about close-game execution

- **Late-game half-court diet:** High PnR (Action A) — `~4 of 6` half-court possessions in chunk 3 are PnR. Horns 1x (poss 4). Iso 1x (poss 6). Motion/4-out 1x (poss 2, 7). **PnR is Montverde's go-to close-game half-court action.** `[CONFIRMED]`
- **Primary close-game handler:** `#3 Tyndale` (~3 of ~6 close-game half-court possessions). **`#2 Miller` is the secondary close-game handler** — handled the PnR on possessions 3 and 8. `[CONFIRMED]`
- **Foul-drawing as scoring mode:** `4 FT trips in chunk 3 alone` (poss 3, 4, 10, 11 — and an additional FT-eligible-but-incomplete foul on poss 9). Montverde leveraged its PnR-to-FT pipeline late. `[CONFIRMED]`
- **Late-game ball-security weakness:** `2 turnovers in the final 1:00` (poss 8 #2 iso TO) is a critical scouting flag. Montverde's PnR-to-iso conversion under pressure is exploitable. `[LIKELY]` (one explicit TO, plus the C1/C2 pattern of #2 / #11 going 1-on-1 under pressure).
- **#11 Delancy as late-clock creator:** Q4 1:35 explicit "play maker too like #3" — `#11` can manufacture a bucket when the shot clock dies. `[SINGLE GAME SIGNAL]` (1 explicit late-clock iso, but consistent with his shot-making throughout the film).
- **Brewster's intentional-foul-to-extend response:** Final ~14 seconds, Brewster fouled immediately three consecutive Montverde possessions. Montverde shot FTs and converted enough to ice the win. **This is the Brewster scouting tip, but Montverde's job late was to make FTs — which they did at a sufficient clip to survive.** `[CONFIRMED]`
- **Player health / availability late:** **#1 Philon cramped at Q4 1:54** and was subbed out at Q4 1:33 for #10 Koulisianis. Montverde's primary scoring forward was unavailable for the final ~90 seconds. The closing lineup was `#3 #2 #11 #10 #42`. `[CONFIRMED]`
- **Confidence on late-game tendencies:** The close-game late-game mode is `[CONFIRMED]` for this film — PnR-centric, FT-leveraging, #3 / #2 as handlers, #11 as late-clock manufacturer, #1 cramped out. The data is unusually rich for a close game.

---

## SECTION 6 — DEFENSE: BASE SCHEME

- **Primary defense:** `pressure man-to-man` — Montverde ran aggressive man-to-man as the base across chunks 0, 1, and 2. Hard close-outs, on-ball pressure, off-ball denial. Per scratchpad: **"pressure man to man defense"** appears as the descriptor on every defensive sequence row in chunks 0–2. Chunk 3 defensive sequence table is empty (Brewster's offensive possessions in the final 3:55 were mostly free throws after intentional fouls). `[CONFIRMED]`
- **Percentage of possessions (approximate):** Man-to-man `~95%` / press `~5%`. Press deployments are extremely rare (one explicit 1-2-1-1 deployment in chunk 0).
- **Scheme posture by quarter:**
  - **Q1 (chunk 0).** Pure pressure man-to-man. Examples: C0 def `Q1 5:45` "pressure man to man defense. hard close out but fouled a shooter," `Q1 4:11` "pressure man to man — #3 steals ball from ball handler," `Q1 2:27` "pressure man to man defense. Solid / good defense. Brewster scores. Good defense." Notable Q1 deployment: **`Q1 0:57` 1-2-1-1 press** — there was a whistle play reset, then switched to man-to-man press that led to a steal. **First and only press appearance.**
  - **Q2 (chunk 1).** Mostly pressure man-to-man. Examples: C1 def `Q2 5:09` "man to man. #1 tips ball from ball handler. #11 steals in," `Q2 3:37` "man to man. Solid defense that leads to a stop." One **full-court press / tap** at `Q2 2:36` — inbounder defender trapped ball, good possession but allowed an offensive rebound + score. Q2 0:28: "lets up a lot of dribble penetration."
  - **Q3 (chunk 2).** Man-to-man under increasing pressure as Brewster comes back. Examples: C2 def `Q3 6:20` "solid man to man defense — forced T.O." `Q3 4:16` "man to man — 3rd possession in a row they get scored on." `Q3 3:18` "2 possessions in a row where Montverde can't convert on loose ball or getting a rebound. 3rd possession for Brewster off this sequence they scored — 50/50 balls." `Q3 1:37` "strong defense, decent covered drive that lets up off-reb score." `Q3 0:03` — **buzzer-beat shot by Brewster #0. "best player can't guard #0."**
  - **Q4 (chunk 3).** Insufficient observation — no defensive sequence rows logged for chunk 3. Brewster's late offense came largely from FT line after intentional fouls, not from designed half-court possessions.
- **Pressure level:**
  - In man (all observed quarters): `pressure` — strong on-ball, denial off-ball, hard close-outs (sometimes fouling the shooter — see C0 def Q1 5:45).
  - Press / trap: `pressure` when deployed (Q1 0:57 1-2-1-1 → steal; Q2 2:36 inbound trap → steal but allowed an OREB-extended score).
- **Off-ball positioning:**
  - In man: `pressure / denial / over-the-top`. Multiple notes about "great at getting through screens" (C0 def Q1 1:16), "good at getting through screens. No makes." `[CONFIRMED]` Montverde's bigs and wings actively fight through off-ball screens.
- **Post defense:** Insufficient observation — no specific post-up defense rows logged. `[NOT OBSERVED]`.
- **Transition defense:** **Mixed — one explicit breakdown.** `Q1 5:01` "pressure man to man hard close out, got beat off dribble, no help — Brewster easy lay up." This is a help-defense breakdown more than pure transition, but Brewster scored in a hurry. Otherwise transition defense not flagged as a systemic weakness. `[SINGLE GAME SIGNAL]` for transition-D breakdowns.
- **Late-game weakness — cannot guard Brewster #0:** **The single most exploitable defensive observation in this film.** Chunk 2 defensive sequence rows explicitly call out:
  - `Q3 0:03` "#0 on Brewster scores again. **best player can't guard #0**. buzzer beat shot. Montverde let up another 2 straight makes prior."
  - `Q4 5:15` "solid defense — took Brewster to final of shot clock. Brewster just makes tough shots. **#0 and #2 shot makes, play makers too.**"
  - **Pattern:** Whoever Montverde assigned as primary on-ball defender (likely #3 Tyndale given size matchup with Brewster #0 Pemberton, the PG) couldn't contain him in the late-Q3 / early-Q4 stretch. Brewster #0 hit 2-3 consecutive shots that triggered the comeback. `[CONFIRMED]` — biggest game-level defensive weakness. (Specific Montverde defender identity flagged in §10c — "best player" is ambiguous.)
- **Other defensive notes:**
  - **Pressure leads to fouls on shooters.** Q1 5:45 "hard close out but fouled a shooter." Hard close-outs are a double-edged sword. `[SINGLE GAME SIGNAL]`.
  - **50/50 ball failure in chunk 2.** Q3 3:18 explicit note — Montverde couldn't win loose balls, leading to Brewster offensive-rebound conversions. `[LIKELY]` — this is part of the comeback dynamic.
- **Confidence:** `[CONFIRMED]` for pressure man-to-man as base across chunks 0–2. `[SINGLE GAME SIGNAL]` for the 1-2-1-1 press (one occurrence). `[CONFIRMED]` for "cannot guard Brewster #0" as the primary defensive exposure. `[NOT OBSERVED]` for chunk-3 defensive posture and for post defense at the per-possession level.

---

## SECTION 7 — DEFENSE: BALL SCREEN COVERAGE

- **Primary coverage:** `drop` — both observed PnR defensive possessions used drop coverage with `#42 Daniels` as the screen defender and `#11 Delancy` as the ball defender. **Caveat:** all observations are in chunk 0 only — chunks 1, 2, 3 have **empty** PnR-coverage tables (only 2 logged PnR defense rows in the entire film). `[LIKELY]` (per "2 occurrences" rule), with strong caveat that observation is single-chunk only.
- **Frequency (of 2 logged PnR defensive possessions, both chunk 0):**
  - `drop` — **2 of 2** (`Q1 6:20` `[2pt make — Brewster hit a pull-up over the drop]`, `Q1 3:52` `[foul drawn on us — Brewster fouled Montverde on the screen]`).
  - No `hedge`, `switch`, `ICE`, `blitz`, or `show` coverages observed.
- **Coverage timeline (did it change during game?):**
  - **Q1 (chunk 0):** Drop primary on both observed PnR possessions. `[LIKELY]`
  - **Q2 (chunk 1) / Q3 (chunk 2) / Q4 (chunk 3):** **No PnR defense rows logged in any of these chunks.** `[NOT OBSERVED]` at the per-possession level. Either (a) Brewster ran fewer PnRs in chunks 1–3, (b) coverage was unremarkable and not logged, or (c) coverage shifted but wasn't captured. Cannot determine which from the scratchpad alone.
- **Coverage by personnel:**
  - **`#42 Daniels`** is the screen defender in both logged PnR possessions. Primary big in PnR coverage.
  - **`#11 Delancy`** is the ball defender in both logged PnR possessions. Primary on-ball PnR defender.
  - **Other personnel:** No PnR coverage with other screen defenders observed. Cannot confirm whether #10 Koulisianis (when subbed in for #42) would also play drop.
- **Execution quality (where does it break down?):**
  - **Drop yielded a Brewster pull-up make at `Q1 6:20`.** #11 got through screen but was a bit behind; #42 was in drop; Brewster hit a pull-up. **Drop-vulnerable to a pull-up shooter.** `[SINGLE GAME SIGNAL]` (1 explicit example, but consistent with the structural weakness of drop coverage).
  - **Drop drew a foul at `Q1 3:52`.** #11 went through the screen hard, drawing a foul. Coverage held but cost a foul. `[SINGLE GAME SIGNAL]`.
- **Confidence:** `[LIKELY]` Montverde defaults to drop coverage in PnR — both observed possessions used it. **CAVEAT:** the entire PnR-defense sample is 2 possessions in chunk 0. Coverage in chunks 1–3 is `[NOT OBSERVED]`. TEX outputs that claim Montverde is a "drop team" with high confidence are over-extending from this small sample. Per Film 03 grading precedent for non-observed PnR defense, chunks 1–3 PnR coverage should be flagged as `[NOT OBSERVED]` rather than assumed.

---

## SECTION 8 — DEFENSE: INDIVIDUAL DEFENSIVE TENDENCIES

*One block per Montverde player who appears repeatedly in defensive sequences. Defensive sequence rows are selective (noteworthy events only), so denominators are unknown. Treat individual defensive tendencies as directional, not precise.*

### #3 — Javion Tyndale (PG, 5'9", Jr 2027)

- **Primary defensive assignment:** Brewster's primary ball-handler in man (almost certainly Brewster #0 Pemberton, the listed PG, given size matchup — flagged in §10c).
- **On-ball quality:** `[CONFIRMED]` **strong / active.** C0 def `Q1 4:11` "pressure man to man — #3 steals ball from ball handler." C1 def `Q2 5:09` "man to man. #1 tips ball from ball handler. #11 steals in" (#3 in lineup but not the steal initiator here). Multiple pressure-based steals attributed to #3.
- **Help activity:** `[LIKELY]` active — appears in lineups across all logged defensive sequence rows.
- **Identified weakness:** **Cannot guard Brewster #0 in the late-Q3 / early-Q4 stretch** — likely the "best player can't guard #0" attribution given his on-ball matchup. Brewster #0 hit multiple shots in succession during the comeback window. `[LIKELY]` for the matchup attribution (see §10c for the ambiguity flag). Size at 5'9" is a structural disadvantage against a 6'1" handler.
- **Confidence:** `[CONFIRMED]` strong on-ball pressure / steal generation. `[LIKELY]` size-and-matchup exposure to Brewster #0 in late-game.

### #11 — Oneal Delancy (G, 6'3", Jr 2027)

- **Primary defensive assignment:** Primary on-ball PnR defender (2 of 2 logged PnRs). Wing in man.
- **On-ball quality:** `[LIKELY]` **above average.** Got through PnR screens hard (Q1 3:52 drew Brewster foul on the screen). C1 def `Q2 5:09` "#11 steals in" (steal attribution).
- **Help activity:** Active — appears in lineups across defensive sequence rows.
- **Identified weakness:** PnR drop coverage left him a step behind the ball-handler at Q1 6:20 → Brewster pull-up make. `[SINGLE GAME SIGNAL]`.
- **Confidence:** `[LIKELY]` for above-average ball-defense overall.

### #2 — Dhani Miller (G, 6'3", Sr 2026)

- **Primary defensive assignment:** Wing in man. Full-court / half-court trap participant (C1 def Q2 2:36 inbounder-defender trap).
- **On-ball quality:** `[LIKELY]` **average to above average.** No specific on-ball steals attributed to #2 alone, but consistent presence in good defensive sequences.
- **Help activity:** **Trap participant.** Q2 2:36 "full court press / tap. Inbounder defender traps ball. Good defensive possession but let up an off-rebound + score" — #2 was in the lineup for this trap deployment.
- **Identified weakness:** None specifically logged. `[NOT OBSERVED]`.
- **Confidence:** `[LIKELY]` for above-average defense.

### #1 — Joe Philon III (F, 6'8", Sr 2026)

- **Primary defensive assignment:** Forward / big-wing in man.
- **On-ball quality:** `[LIKELY]` — C1 def `Q2 5:09` "#1 tips ball from ball handler" — generated a deflection / steal.
- **Help activity:** Limited specific observations beyond lineup presence.
- **Identified weakness:** **Health / availability:** cramped at Q4 1:54, subbed out at Q4 1:33 for the final ~90 seconds. Not a defensive tendency per se but affects late-game defensive personnel. `[CONFIRMED]`
- **Confidence:** `[LIKELY]` for active defense including steals / deflections.

### #42 — Derek Daniels (C, 6'8", Jr 2027)

- **Primary defensive assignment:** Primary PnR screen defender (drop coverage — 2 of 2 logged). Rim protector.
- **On-ball quality:** `[LIKELY]` drop-defender — sat back on both observed PnRs.
- **Help activity:** `[LIKELY]` rim protection from drop position. No specific block / rotation observations logged.
- **Identified weakness:** **Drop coverage vulnerable to pull-up shooters** — Q1 6:20 Brewster pull-up over the drop. `[SINGLE GAME SIGNAL]` (but structurally consistent with drop coverage's known weakness).
- **Confidence:** `[LIKELY]` for drop-coverage execution as observed.

### #10 — Nikos Koulisianis (F, 6'9", Sr 2026)

- **Primary defensive assignment:** Backup big behind #42. Late-game replacement for #1 (Q4 1:33 sub-in for cramping #1).
- **On-ball quality:** Insufficient observation — no PnR defense rows logged when #10 was in the game.
- **Help activity:** Insufficient observation. `[NOT OBSERVED]`.
- **Confidence:** `[NOT OBSERVED]` for individual defensive tendencies.

### Summary — team-level defensive tendencies

- **Pressure man-to-man + active on-ball + denial off-ball.** The base defensive identity is high-pressure, deny-everything man. Multiple "pressure man to man defense" / "great at getting through screens" notes. `[CONFIRMED]`
- **Cannot guard Brewster #0 down the stretch.** The single most actionable scouting note. Late-Q3 / early-Q4 buzzer-beat sequence + the Q4 5:15 "#0 and #2 [Brewster] play makers too" exposure. **Whoever was on #0 (most likely #3) got beat repeatedly.** `[CONFIRMED]`
- **50/50 ball failure in the comeback window.** Q3 3:18 "Montverde can't convert on loose ball or getting a rebound" → Brewster comeback fuel. `[LIKELY]` — directly attributed to the comeback.
- **Drop coverage in PnR — vulnerable to pull-up shooters.** Single-chunk sample but consistent. `[LIKELY]`
- **Aggressive close-outs occasionally produce fouls on shooters.** Q1 5:45 example. `[SINGLE GAME SIGNAL]`.
- **Press deployment is rare / situational.** Single 1-2-1-1 press in entire film. NOT a base posture. `[CONFIRMED]` rare.

---

## SECTION 9 — INDIVIDUAL PLAYER CONSOLIDATED PROFILES

*One block per Montverde player with 10+ observed offensive possessions. Foundation for the
"Player Pages" section of the final report.*

### #3 — Javion Tyndale (seeded PG, 5'9", Jr 2027) — **the lead PG / primary creator**

- **Total possessions observed:** `~60+` (on floor for nearly the entire game — appears as initiator / handler across all 4 chunks). Played essentially wire-to-wire.
- **Confirmed position from film:** `PG` — primary ball-handler confirmed. Only sub-6'0" Montverde player on the floor; obvious lead-handler size.
- **Confirmed dominant hand from film:** **Insufficient observation** — handedness not explicitly noted on drives or pull-ups. `[NOT OBSERVED]`.
- **Confirmed role:** `primary_initiator` / `creator` / `scorer-passer hybrid`.
- **Offensive role (specific):** **The hub of Montverde's offense.** Initiates the majority of Horns and 1-4 flat / High PnR possessions. Brings ball up nearly every possession. Comes off ball screens, drives, pulls up, kicks out, sets up the action. Scratchpad note at C0 row 12: "#3 drive kicks for 3pt make. Pass was a little out of control. **#3 is small. Sometimes hard to make the passes he does.**" Plays through his size — generates plays even when the passing window is tight.
- **Scoring zones with frequency:**
  - Rim: `~3 of ~5` — multiple driving layups and finishes (C0-9 tough shot, C1-7 PnR tough layup, C1-8 transition layup, C1-12 lob-pass-but-scorer-was-#10).
  - Paint (non-rim): `~0 of ~1`.
  - Mid-range: `~0 of ~1`.
  - 3pt: **`~3 of ~6`** — C0-5 (`Q1 5:34` horns 3pt make, no passing, just used screen), C0-12 (`Q1 1:46` horns 3pt make off drive-and-kick), C2-7 (`Q3 4:30` Horns 3pt miss). **Multi-game 3pt threat off Horns / motion.**
  - FT attempts: `~3+ trips` (C0-16 FT 1/2, C2-20 FT 1/2 from PnR, C3-9 to C3-11 cluster on intentional fouls).
- **Shot chart location summary:** Multi-level scorer despite small size. Will hit a 3 when motion or Horns produces it. Drives are typically tough-shot or kick-out. Foul-drawer late.
- **Key tendencies (each tagged with confidence + count):**
  - **Primary initiator across all 4 chunks** `[CONFIRMED]` (~25+ explicit initiator attributions in the possession tables).
  - **3pt shooter off Horns / motion screens** `[CONFIRMED]` (3 explicit makes — C0-5, C0-12, plus the make on C0-18 which #11 finished but #3 initiated).
  - **Drives + kicks out for shooters** `[CONFIRMED]` (multiple drive-and-kick possessions ending in 3pt makes for teammates).
  - **Pushes ball in transition** `[CONFIRMED]` (C1-8 transition layup, C1-13 transition push to #42, C2-11 transition push to FT).
  - **Small size makes tight passes risky** `[LIKELY]` (explicit scratchpad note at C0-12 + visible TO at C0-6 from a forced pass in paint).
  - **Late-clock decision-maker** `[LIKELY]` (chunk-3 PnR handler 2 of ~6 close-game half-court possessions; partner with #11 for late-clock creation).
- **Defensive assignment:** Primary on-ball defender for Brewster's ball-handler. Strong on-ball pressure + steals (Q1 4:11 explicit steal).
- **Defensive vulnerability:** Likely the "best player can't guard #0" attribution — size at 5'9" against a bigger handler. `[LIKELY]`.
- **Free throw shooting observed:** ~3 trips, makes per-trip varied.
- **Turnovers:** `~3` clean attributable (C0-6 bad pass after PnR drive, C0-17 forced back-door pass in DHO, C2-12 stripped on PnR refuse, C2-13 moving screen on high PnR).
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 5:34` — Horns 3pt make, no passing, used screen.
  - `C0 · Q1 1:46` — Horns drive-and-kick 3pt make.
  - `C1 · Q2 3:51` — Transition 2-on-1 push, ball poked + recovered + layup finish.
  - `C2 · Q3 2:04` — Transition push + great pass leading to FT 2-of-2.
  - `C3 · Q4 1:35` — Set up late-clock iso for #11 (paired playmaking).

### #1 — Joe Philon III (seeded PF, 6'8", Sr 2026) — **the multi-level scoring forward**

- **Total possessions observed:** `~50+` (starter; out Q2 2:08 → halftime, and Q4 1:33 → end for cramping). Heavy minutes when available.
- **Confirmed position from film:** `F / scoring forward` — seeded as PF, observed as a 3-level scoring forward. Pops to elbow on BLOBs, hits 3s, drives baseline, scores inside off lobs. **Not a traditional interior PF — operates more as a wing-forward / 4-out big.** Flagged in §10d.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `primary_scorer` / `multi-level scoring forward` / `BLOB receiver`.
- **Offensive role (specific):** **Montverde's primary scoring forward.** Catches lobs from #2 (C0-1 alley-oop dunk attribution — though row 1 lists #2 as initiator, the dunk receiver was #42 per the note; #1 separately catches lobs elsewhere). Pops to elbow on BLOBs (4-across formation — Q3 5:27, Q4 7:01). Hits 3s (C2-21 Q4 4:51 3pt make off PnR kick-out). Drives baseline (C0-7 baseline drive for layup attribution — though row 7 lists #11; #1 separately drives elsewhere). Scores inside off BLOB action (C0-13 BLOB and-1).
- **Scoring zones with frequency:**
  - Rim: `~3 of ~4` — C0-13 (Q1 1:01 BLOB and-1 paint score), C0-14 (Q1 0:42 transition dunk attribution per row note "#1 got ball in transition for drunk"), and rim finishes off motion.
  - Paint (non-rim): `~1 of ~2`.
  - Mid-range: `~0 of ~1`.
  - 3pt: `~1 of ~3` — C2-21 (`Q4 4:51` 3pt make from PnR kick-out), C0-2 attribution to #1 finishing on screen-the-screener (likely a midrange jump shot).
  - FT attempts: `~3+ trips` (C0-13 BLOB and-1 FT, C3-10 intentional-foul FT — but see §10c attribution flag).
- **Shot chart location summary:** **3-level forward.** Rim threat off BLOBs and transition. Mid-range / elbow-pop threat. 3pt range from kick-outs. **The most diverse scoring profile on the roster.**
- **Key tendencies (each tagged with confidence + count):**
  - **Elbow popper / BLOB receiver** `[CONFIRMED]` (Q3 5:27 + Q4 7:01 both feature #1 popping to elbow from baseline — twice explicitly logged).
  - **BLOB and-1 scorer** `[SINGLE GAME SIGNAL]` (C0-13 Q1 1:01 — one explicit and-1 from BLOB, but it's the cleanest scoring BLOB in the film).
  - **3pt threat off PnR kick-out** `[SINGLE GAME SIGNAL]` (C2-21 Q4 4:51 — one explicit make).
  - **Lob target on motion / 4-out 1-in** `[LIKELY]` (C0-1 alley-oop attribution ambiguous between #1 and #42 — see §10c).
  - **Health risk:** **Cramps at Q4 1:54** — subbed out Q4 1:33. Closing minutes liability. `[CONFIRMED]`.
- **Defensive assignment:** Forward / big-wing in man.
- **Defensive vulnerability:** Health — see above.
- **Free throw shooting observed:** ~3 trips.
- **Turnovers:** `0 cleanly attributable` (C0-3 attributes the TO to #11, not #1, despite #1 being in lineup).
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 1:01` — BLOB and-1 in paint (the cleanest BLOB score).
  - `C0 · Q1 0:42` — Transition dunk attribution.
  - `C2 · Q4 4:51` — PnR kick-out 3pt make.
  - `C2 · Q4 7:01` — BLOB elbow-pop → feeds #42 in post for layup.
  - `C3 · Q4 1:54` — **Cramping incident, subbed out.**

### #2 — Dhani Miller (seeded PG, 6'3", Sr 2026) — **the secondary handler / scoring guard**

- **Total possessions observed:** `~50+` (starter throughout). Heavy minutes.
- **Confirmed position from film:** `SG / scoring guard` — **not the primary PG** despite seeded position. Operates as a scoring guard and secondary ball-handler / PnR-handler when #3 is off-ball. Flagged in §10d.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `secondary_initiator` / `scoring guard`.
- **Offensive role (specific):** Secondary handler. Receives BLOB inbound passes (C0-13 inbounder). Runs high PnR with #42 (C2-21 Q4 4:51 kick-out 3pt make for #1 as the scorer; C3-3 Q4 2:42 drive + FT trip; C3-8 Q4 0:39 PnR 1-on-1 TO). Hits transition pull-up 3s (C1-1 Q2 6:04 transition pull-up 3pt miss). Drives into zone middle (C1-11 Q2 2:05 dunk dump to #42, but attribution per row says #2 initiator).
- **Scoring zones with frequency:**
  - Rim: `~1 of ~3` — C0-1 (alley-oop pass to #42, scorer = #42 — but #2 was the playmaker initiator).
  - Mid-range: `~0 of ~0`.
  - 3pt: `~1 of ~3` — C1-1 transition pull-up 3pt miss, C0-4 Q1 6:08 3pt make off DHO action (per row: "#11 drove right baseline and kicked it back to #2 top of key for open 3pt make").
  - FT attempts: `~2+ trips` (C3-3 Q4 2:42 FT 2/2).
- **Shot chart location summary:** Scoring guard with PnR-handler responsibilities. Hits open 3s off kick-outs. Drives the PnR for FT trips. Can be turnover-prone late (C3-8 PnR 1-on-1 TO).
- **Key tendencies (each tagged with confidence + count):**
  - **Secondary PnR handler with #42** `[CONFIRMED]` (~4 of 17 PnRs — C2-21, C3-3, C3-8, plus C2-14 1-4 flat double high PnR).
  - **Late-game closer / Brewster intentional-foul target** `[CONFIRMED]` (handled the ball during Brewster's late foul-to-extend sequence — was the PnR handler at Q4 0:39 immediately before the intentional fouls started).
  - **3pt shooter off DHO kick-out** `[LIKELY]` (C0-4 Q1 6:08 explicit).
  - **Inbounder on BLOB** `[LIKELY]` (C0-13 inbound attribution).
  - **PnR-to-iso TO under pressure** `[SINGLE GAME SIGNAL]` (C3-8 Q4 0:39 explicit late-game iso TO).
- **Defensive assignment:** Wing in man. Trap participant (Q2 2:36).
- **Defensive vulnerability:** Not specifically called out. `[NOT OBSERVED]`.
- **Free throw shooting observed:** ~2 trips.
- **Turnovers:** `~1` cleanly attributable (C3-8 Q4 0:39 PnR iso TO).
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 8:00` — Lob pass to #42 for alley-oop dunk (initiator credit per Tommy's convention).
  - `C0 · Q1 6:08` — Open 3pt make off DHO kick-out.
  - `C2 · Q4 4:51` — High PnR creating #1's kick-out 3pt make.
  - `C3 · Q4 2:42` — High PnR drive + FT 2/2 (close-game possession).
  - `C3 · Q4 0:39` — PnR 1-on-1 TO under Brewster pressure (critical late TO).

### #11 — Oneal Delancy (seeded PG, 6'3", Jr 2027) — **the secondary handler / shot-maker**

- **Total possessions observed:** `~55+` (starter throughout). Heavy minutes.
- **Confirmed position from film:** `G / combo guard` — secondary handler / scoring guard. Initiates as both handler and screen-receiver. Slightly more on-ball than off-ball.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `secondary_initiator` / `slasher` / `late-clock creator`.
- **Offensive role (specific):** **The other half of the Tyndale-Delancy lead-guard tandem.** Drives baseline (multiple — C0-3 baseline drive though that ends in a TO; C0-7 baseline drive for layup; C2-19 left-wing drive for open layup). Runs PnR (C0-4 right-baseline drive + kick to #2 for 3pt make; C1-2 horns continuation PnR; C2-1 4-out drive). **Late-clock 1-on-1 creator** (C3-6 Q4 1:35 late-clock iso 2pt make — explicitly noted "play maker too like #3"). Pulls up in transition (C1-4 receives transition pass for layup).
- **Scoring zones with frequency:**
  - Rim: `~5 of ~7` — C0-7 (`Q1 4:32` baseline drive layup), C1-2 (`Q2 5:48` PnR pull-up 2pt make), C1-4 (`Q2 5:04` transition layup), C2-19 (`Q4 6:13` PnR-induced layup), C3-1 (`Q4 3:55` out-of-BLOB tough shot make), C3-6 (`Q4 1:35` late-clock iso 2pt make).
  - Paint (non-rim): `~0 of ~1`.
  - Mid-range: `~0 of ~1` (C1-2 pull-up was attributed as 2pt make — could be paint or mid).
  - 3pt: `~1 of ~2` — C0-18 (`Q2 6:33` Horns/DHO 3pt make — receiver was #11 finishing the drive-and-kick that came from #42's DHO action).
  - FT attempts: `~1+ trips` (C3-4 Q4 2:14 Horns FT 2/2).
- **Shot chart location summary:** Driver / finisher first. 3pt shooter when the play creates one. Late-clock tough-shot maker.
- **Key tendencies (each tagged with confidence + count):**
  - **Baseline driver** `[CONFIRMED]` (C0-7, C2-19, plus C0-3 baseline-drive TO — pattern is real, even when not converting).
  - **Late-clock 1-on-1 creator** `[SINGLE GAME SIGNAL]` (C3-6 Q4 1:35 explicit; consistent with overall shot-making profile).
  - **PnR handler from non-flat alignments** `[LIKELY]` (~3 PnRs as handler — C0-4, C1-2, C2-19).
  - **Transition finisher / runner** `[LIKELY]` (C1-4 transition pass-ahead layup).
  - **Tough-shot maker out of BLOB** `[SINGLE GAME SIGNAL]` (C3-1 Q4 3:55 tough well-guarded shot to start chunk 3).
- **Defensive assignment:** Primary on-ball PnR defender (2 of 2 logged). Wing in man.
- **Defensive vulnerability:** PnR drop coverage left a step behind ball-handler at Q1 6:20 → Brewster pull-up make.
- **Free throw shooting observed:** ~1 trip.
- **Turnovers:** `~1` (C0-3 Q1 6:35 baseline drive, dumped to #42 in post, defender stole ball — TO credit to #11).
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 4:32` — 4-out baseline drive for layup.
  - `C0 · Q2 6:33` — Horns/DHO drive-and-kick converted into open 3pt make (#11 was the kick-out shooter per row note).
  - `C1 · Q2 5:48` — Horns PnR pull-up 2pt make.
  - `C2 · Q4 6:13` — 5-out / PnR drive for open layup ("called for PnR... and #42 shows then cuts and #11 drives open layup").
  - `C3 · Q4 3:55` — Tough well-guarded shot to open chunk 3 (close-game momentum-setter).
  - `C3 · Q4 1:35` — **Late-clock iso 2pt make — "#11 play maker too like #3."**

### #42 — Derek Daniels (seeded C, 6'8", Jr 2027) — **the primary big / screen-and-roll engine**

- **Total possessions observed:** `~50+` (starter; subbed out Q2 5:51 to Q2 2:08 — ~4 min off floor in chunk 1). Heavy minutes otherwise.
- **Confirmed position from film:** `C / 5` — primary big. Screen-setter, roller, post-up option, BLOB target.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `screener` / `roller` / `post-finisher`.
- **Offensive role (specific):** **The screen-and-roll engine of the Montverde offense.** Primary screener in High PnR (Action A) — ~12 of ~17 PnRs feature #42 as screener. DHO partner in Horns (Action B). Rolls hard, finishes at rim, posts up when fed. Strong physically — scratchpad explicitly notes "#42 very strong" at C1-13. Scores off lobs (C0-1 alley-oop dunk receiver), receives feeds in post (C2-18 Q4 7:01 post layup), rolls for layups, and seals on OREB chases.
- **Scoring zones with frequency:**
  - Rim: `~5 of ~6` — C0-1 (`Q1 8:00` alley-oop dunk), C0-3 attribution (dumped to in post but stolen — TO credit), C1-11 (`Q2 2:05` zone-middle dunk dump from #2), C1-13 (`Q2 0:45` transition rim finish — "#42 very strong"), C2-18 (`Q4 7:01` post layup off BLOB feed from #1), C1-12 (`Q2 1:13` 1-4 flat high PnR — though the lob recipient was #10 here, not #42).
  - Paint (non-rim): `~0 of ~0`.
  - Mid-range: `~0 of ~0`.
  - 3pt: `~0 of ~0` — does not shoot from deep.
  - FT attempts: `~2+ trips` (C2-20 Q4 5:35 FT 1/2 from PnR roll, C3-11 Q4 0:04 FT detail TBD per §10b).
- **Shot chart location summary:** Rim only. Roller, post-sealer, lob target.
- **Key tendencies (each tagged with confidence + count):**
  - **Primary High PnR screener with #3 (and #2)** `[CONFIRMED]` (~12 of ~17 PnRs).
  - **DHO partner in Horns** `[CONFIRMED]` (C0-18 explicit; multiple Horns possessions list #42 at elbow).
  - **Lob / alley-oop receiver** `[LIKELY]` (C0-1 explicit alley-oop dunk; C1-12 lob is actually to #10 per row note).
  - **Post-up finisher when fed off action** `[LIKELY]` (C2-18 Q4 7:01 post layup off BLOB feed, C1-11 dunk dump from zone-middle).
  - **Physically strong** `[CONFIRMED]` (explicit scratchpad note at C1-13 "very strong").
  - **Transition runner who fills the lane** `[LIKELY]` (C1-13 transition rim finish).
- **Defensive assignment:** Primary PnR screen defender (drop coverage). Rim protector.
- **Defensive vulnerability:** Drop coverage vulnerable to pull-up shooters (Q1 6:20 example).
- **Free throw shooting observed:** ~2 trips.
- **Turnovers:** `~1` cleanly attributable (C2-6 Q3 5:07 "2 on elbow 2 in corner — miscommunication on a pass T.O.").
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 8:00` — Alley-oop dunk off motion lob from #2.
  - `C1 · Q2 2:05` — Dunk dump from #2's zone-middle attack.
  - `C1 · Q2 0:45` — Transition rim finish — "very strong."
  - `C2 · Q4 5:35` — Roll-man finish off PnR with #3 → FT 1/2.
  - `C2 · Q4 7:01` — Post layup off BLOB feed from #1.

### #10 — Nikos Koulisianis (seeded PF, 6'9", Sr 2026) — **the backup big / late-game closer**

- **Total possessions observed:** `~15+` (subbed in for #42 at Q2 5:51 for ~4 minutes; subbed in for #1 at Q4 1:33 for the final ~90 seconds). Limited but meaningful minutes.
- **Confirmed position from film:** `F / backup big` — operates as the second big when #42 sits, or as a closer alongside #42 when #1 is unavailable.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `screener` / `roller` / `late-game closer`.
- **Offensive role (specific):** Backup big role — sets ball screens (C1-2 listed as a screener in horns continuation), receives lobs (C1-12 Q2 1:13 1-4 flat high PnR — "#3 goes opposite of screen drives to paint and lob to #10 for layup" — explicit lob recipient). Late-game closer (Q4 1:33 → end). Did not have a designed shot attempt in chunk 3.
- **Scoring zones with frequency:**
  - Rim: `~1 of ~1` — C1-12 (`Q2 1:13` lob layup `[2pt make]`).
  - 3pt: `~0 of ~0`.
  - FT attempts: insufficient observation.
- **Shot chart location summary:** Rim only (small sample). Lob recipient.
- **Key tendencies (each tagged with confidence + count):**
  - **Lob recipient on 1-4 flat high PnR** `[SINGLE GAME SIGNAL]` (C1-12 only — one explicit).
  - **Late-game closer when #1 unavailable** `[SINGLE GAME SIGNAL]` (Q4 1:33 sub-in for cramping #1 — situational, but he was the chosen closer).
  - **Mid-Q2 spell for #42** `[LIKELY]` (Q2 5:51 → Q2 2:08 sub run).
- **Defensive assignment:** Backup big.
- **Defensive vulnerability:** Insufficient observation. `[NOT OBSERVED]`.
- **Free throw shooting observed:** insufficient observation.
- **Turnovers:** `0 cleanly attributable`.
- **Notable plays (timestamps for the grading UI):**
  - `C1 · Q2 1:13` — Lob layup off #3's 1-4 flat high PnR (his only logged make).
  - `C3 · Q4 1:33` — Subbed in for cramping #1 Philon. Closing-lineup big.

### Montverde roster — players who DID NOT APPEAR or had insufficient observation

- **`#12 Sebastien Ndour`** — `1 logged possession` (C1-15 Q2 0:02 BLOB initiator on a 3-across alley-oop attempt that missed). Subbed in at Q2 0:21 for #10. Below 10-possession threshold for a player profile block. Status: `insufficient observation`.
- **`#5 Lincoln Cosby`, `#25 Trace Lopez`, `#32 Malachi Booker`, `#33 Jayden Hodge`** — NO possessions observed in any chunk. Either DNPs or garbage-time below observation threshold. Status: `not_evaluated`.

### Unknown players (seen on film but not on seeded roster)

| # | Short description | Suggested name (if known) | Possessions observed |
|---|---|---|---|
|   | *(none — all 7 observed Montverde jerseys (#1, #2, #3, #10, #11, #12, #42) match the seeded roster)* |   |   |

---

## SECTION 10 — SYNTHESIS FLAGS

*Every judgment call you made. Every uncertainty. Every vocabulary reconciliation. Every contradiction resolved. Listing them here is what makes the ground truth honest.*

### 10a — Vocabulary reconciliations

- **"1-4 flat" / "1-4 flat high PnR" / "1-4 flat double high PnR" / "high PnR" / "PnR" (in flat-alignment context) / "1-4 floor" (C2-16 scratchpad typo)** were used interchangeably across chunks 0–3 to describe what is structurally the same action: 1-4 flat alignment + high PnR with #42 (or #10) as screener. Unified in §2 as **"Action A: 1-4 flat / High PnR"** with total count ~17. This is Montverde's dominant half-court action.
- **"Horns" / "horns / DHO" / "horns/DHO" / "Low horns"** unified in §2 as **"Action B: Horns / Horns-DHO"** (count ~10). The DHO embedded inside Horns is structural, not a separate set. "Low horns" (C1-16) is the same set with slightly lower elbow positioning.
- **"4 out 1 in" / "5 out" / "motion" / "4 down" / "left side overload" / "4 flat" (in non-BLOB contexts)** unified in §2 as **"Action C: 4-out 1-in / 5-out / motion"** (count ~14). Pass-and-cut-opposite continuity with occasional embedded screens. **Boundary with Horns is real but ambiguous** — C0-2 ("motion" with screen-the-screener for #1 at elbow) overlaps structurally with Horns flow. Kept as motion per Tommy's labeling.
- **"transition" / "transition pull up 3" / "transiton" (typo)** unified in §2 as **"Action D: Transition / push"** (count ~9 opportunities).
- **"iso" / "late-clock iso"** unified in §2 as **"Action E: Iso / late-clock 1-on-1"** (count 1, SGS).
- **"BLOB" with various baseline formations** consolidated in §4 by formation type — 4-flat (3x), stacked (1x), 3-across (1x), block/corner/elbow/top spread (2x). All BLOBs come from "special situations" rows + main possession rows.
- **"pressure man to man defense"** is the single descriptor across all chunks 0–2 for the base defense. Unified in §6 as "pressure man-to-man." The C0 Q1 0:57 "1-2-1-1 press" is treated separately as a one-time deployment.
- **"play maker" / "play maker too like #3"** — used to describe both #3 Tyndale (implicitly) and #11 Delancy (C3-6 explicit). Unified in §9 as a tendency for #11 ("late-clock 1-on-1 creator") that mirrors #3's primary-creator role.
- **"best player can't guard #0"** (C2 def Q3 0:03) — the "best player" referent is ambiguous. Most likely #3 Tyndale given size matchup with Brewster #0 Pemberton, but could also refer to Montverde's "best defender" generically. Flagged in §10c.

### 10b — Counts you are not confident on

- **Per-possession personnel** — chunks 0–3 list 5-jersey lineups for every Montverde offensive possession, but the "same" shorthand breaks down in two places:
  - **C1 row 15 (Q2 0:02)** personnel is listed as "same" (= #3 #2 #10 #11 #42 from row 11) but the Q2 0:21 sub note ("#12 for #10") puts #12 in by Q2 0:02. Actual personnel should include #12, not #10. Flag.
  - **C3 row 10 (Q4 0:10)** lists initiator as #1 even though #1 was subbed out at Q4 1:33 (cramping). Either #1 came back in unlogged, or the initiator label is misattributed. Flag.
- **Defensive sequence rows** — only noteworthy events are logged, NOT every Brewster possession. The denominator for Montverde defensive efficiency is unknown; only qualitative observations are valid. Chunk 3 has **zero** defensive sequence rows logged — most of Brewster's late-game offense came from FT line after intentional fouls, not designed possessions.
- **Montverde team fouls / players in foul trouble** — all live-tracked foul fields are empty across all 4 chunks. **Foul-trouble information is NOT reconstructable from this watch notes file.** Any claim about Montverde foul trouble in TEX's output should be flagged as not graded.
- **OREB tally** — only chunk 2 has an explicit OREB count (1, with the 2nd-chance points = 1 score / 2 pts on C2-14). Chunks 0, 1, 3 OREB tallies are empty in the live-tracked sections. Per the watch-notes wrap-up, total OREBs is "at least 1 confirmed (C2 row 14); C0/C1/C3 not tallied yet." `[LIKELY]` directional, `[NOT OBSERVED]` exact count.
- **FT trips / attempts / makes** — chunk totals per watch-notes wrap-up: 2/3/2, 1/2/2, 4/8/6, 4/6/5 (with C3 row 11 detail TBD: true attempts/makes may be slightly higher → 4/7/6 or 4/8/6). **Whole-game = 11 / 19 / 15 (with TBD).** `[LIKELY]` on exact, `[CONFIRMED]` on directional.
- **Brewster forced TOs (Montverde-induced)** — only tick-marked partially (chunk 0: 1, 2; chunk 1: 1; chunk 3: 1). Total Montverde-forced TOs is `~4` directionally, not a precise count.
- **Brewster transition opportunities / scores** — only chunk 0 (1 opp / 1 score) and chunk 2 (2 opps / 0 scores) and chunk 3 (empty) logged. Chunks 1 is empty. **Likely under-tracked**; don't trust the live-tracked tally as a precise count.
- **Possession ball-screen coverage in chunks 1, 2, 3** — all three chunks have empty PnR-coverage tables. PnR defense inventory is only directly observable for chunk 0 (2 logged possessions). Montverde's PnR defense in chunks 1–3 is `[NOT OBSERVED]` at the per-possession level.
- **C3 row 11 FT detail** — "FT (detail TBD — verify if this should be 4/7/6 or 4/8/6)" per watch notes. Final score works out consistent with at least 1 FT make. Treat as `[LIKELY]` directional.

### 10c — Jersey numbers you could not confirm

- **Brewster jersey numbers are largely unidentified.** Scratchpad references Brewster events by team ("Brewster scored," "Brewster ball-handler") rather than specific jerseys. The major exception is **Brewster #0 Pemberton** — explicitly called out as the unguardable matchup in chunk 2. Beyond #0, Brewster jerseys are out of scope.
- **"Best player can't guard #0" — Montverde defender attribution ambiguous.** C2 def Q3 0:03 / Q4 5:15 calls out Brewster #0 as scoring repeatedly. The Montverde defender most likely matched up on Brewster #0 (PG vs PG) is `#3 Tyndale`, but the scratchpad does not name the defender explicitly. **Could also refer to:** the team's best perimeter defender (could be #11 or #1). Treat the matchup attribution to #3 as `[LIKELY]`, not `[CONFIRMED]`.
- **C0 row 14 (Q1 0:42 transition) — initiator vs. scorer attribution.** Row lists initiator as `#3`, but note text says "#1 got ball in transition for drunk" (typo for "dunk"). Per Tommy's initiator convention (passer / playmaker, not scorer), #3 is the correct initiator (likely the outlet passer), but #1 is the scorer. Resolved.
- **C0 row 1 (Q1 8:00 alley-oop dunk) — scorer attribution.** Initiator listed as #2 (who made the lob pass). The note says "giving #42 a alley oop lob for dunk." So the dunk scorer is #42, not #1 as briefly suggested elsewhere. Resolved in §2 Action C and §9.
- **C3 row 10 (Q4 0:10) initiator = #1, but #1 was subbed out.** Q4 1:33 sub note says "#10 for #1." So at Q4 0:10, #1 should be on the bench. Either (a) #1 came back in unlogged, (b) the FT shooter / initiator label is misattributed (could be #10, or #11, or #2), or (c) the sub note is wrong about the time. **Cannot resolve from the scratchpad.** Flag.
- **C2 row 5 (Q3 5:24 BLOB) initiator = #2, but the play description has #1 popping to elbow on the adjacent row 4.** Two consecutive BLOBs — row 4 with #1 as inbounder-or-popper, row 5 with #2 as initiator on a different formation. Different formations / different roles. Resolved.
- **C2 row 14 (Q4 0:23 OREB → 2pt make).** Initiator = #2, screener = #3. **This is unusual** — #3 setting a ball screen for #2 (reverse of the usual #2-or-#3 + #42 PnR). The play description supports it ("#3 sets right ball screen pops"). Resolved — Montverde does occasionally invert the screener relationship.

### 10d — Contradictions resolved (and how)

- **#1 Joe Philon III seeded as PF vs. observed role as scoring forward / wing-big.** Seeded as PF (6'8" Sr), but observed popping to elbow on BLOBs (Q3 5:27, Q4 7:01), hitting 3s (C2-21), and scoring in transition + paint. **Resolution:** **#1 is a multi-level scoring forward (3-level shooter), NOT a traditional interior PF.** His role is closer to a stretch-4 / scoring wing-forward. Update roster position post-watch.
- **#3 Tyndale as PG (seeded) vs. PG (observed).** Confirmed match — no contradiction. **The only sub-6'0" Montverde player is the lead PG, as expected.**
- **#2 Miller as PG (seeded) vs. SG / scoring guard (observed).** Seeded as PG (G), but film clearly shows #3 as primary handler. **Resolution: #2 is the SG / secondary handler.** Update roster position post-watch.
- **#11 Delancy as PG (seeded) vs. combo guard / shot-maker (observed).** Seeded as PG (G), observed as a combo guard who handles, drives, and shoots. **Resolution: #11 is a combo guard** — not a pure PG, but not exclusively SG either. He pairs with #3 as a lead-guard tandem.
- **Montverde's offense: "no set" (per Films 01 / 02 prior expectation) vs. "multiple structured sets" (per film).** **Resolution: Montverde DOES run multiple structured half-court sets** (1-4 flat / High PnR, Horns, 4-out 1-in motion, BLOB family). Real finding, consistent with Film 03's well-coached prep-program pattern. Don't force "no set" conclusions from Films 01 / 02.
- **Defense: pure m2m vs. occasional press.** **Resolution: pressure m2m is the base; press is `[SINGLE GAME SIGNAL]` situational** (one explicit 1-2-1-1 at Q1 0:57). Don't elevate the press to a base scheme.
- **Game shape: blowout (per first-half 16-pt Montverde lead) vs. close late (per Q4 1-pt margin).** **Resolution: BOTH true at different times.** Montverde controlled the first half, Brewster came back in Q3–Q4, Montverde survived. Game was close late despite an early Montverde double-digit lead. Per Tommy's wrap-up: "wire-to-wire control → Brewster comeback → Montverde survives."

### 10e — Situations that may not be representative

- **Brewster intentional-foul sequence in the final ~14 seconds (C3 rows 9, 10, 11).** Brewster fouled Montverde immediately on three consecutive possessions to extend the game. These are NOT base half-court possessions. Any TEX output that treats these as designed offensive plays is mis-categorizing. **Tag chunk 3 possessions 9, 10, 11 as "intentional-foul-extension free-throw possessions" rather than base offense.**
- **#1 Philon cramping at Q4 1:54.** Affects late-game personnel (closing lineup is #3 #2 #11 #10 #42 instead of #3 #2 #11 #1 #42). Montverde's primary scoring forward was unavailable for the final ~90 seconds. Any close-game tendency claims drawn from those 90 seconds need this asterisk.
- **Brewster's late-Q3 / early-Q4 comeback window.** The 2-pt → -1 swing between Q3 6:21 (Q3 end MV 58–49) and Q4 2:47 (MV 68–69) is the inflection of the game. Multiple Montverde defensive breakdowns cluster in this window (Q3 0:03 buzzer-beat, Q4 5:15 #0 + #2 makes). Pattern is `[CONFIRMED]` (Montverde cannot guard Brewster #0 down the stretch), but the magnitude of the run is partly Brewster execution (tough shots), not pure Montverde collapse.
- **Reactive 1-2-2 zone offense possessions (C1-9, C1-10, C1-11, C2-9).** Brewster played 1-2-2 zone defense for parts of Q2 and Q3, forcing Montverde into a 2-2-1 / "guards-up" zone-offense response. **These are reactive possessions, not base half-court actions.** Tag as zone-offense variants rather than base-offense variants. Sample is too small (4 possessions) to draw zone-offense conclusions beyond "Montverde can find the middle and dump down to #42 for a dunk."
- **#42 / #10 minute split.** #42 played most minutes; #10 subbed in twice (Q2 5:51 → Q2 2:08, Q4 1:33 → end). The PnR action runs through whichever big is on the floor. When grading, don't penalize TEX for attributing actions to either #42 or #10 as long as the player on the floor is correctly identified for each possession.

### 10f — Things you want TEX to get right (watch-items for grading)

1. **Montverde DOES have multiple structured half-court sets.** 1-4 flat / High PnR (~17), Horns (~10), 4-out 1-in / motion (~14), BLOB family (7+ designed BLOBs). Any TEX output that says "no real set offense" or "default to iso" is hallucinating from Films 01 / 02 priors. **The structure is real and multi-action — even more structured than Spire in Film 03.**
2. **High PnR with #3 + #42 is the dominant half-court action.** ~17 occurrences, primary late-game weapon. TEX must identify #42 as the primary PnR screener and #3 as the primary PnR handler (with #2 as secondary).
3. **Horns is the second-most-frequent named set.** ~10 occurrences with heavy weighting in chunk 0. TEX must identify Horns by name — it's structurally distinct from 1-4 flat (two elbows occupied vs. one big at top).
4. **#3 Tyndale is the lead PG / primary creator.** Smart, patient, drives + kicks + shoots 3s + pushes in transition. Hub of the offense across all 4 chunks. TEX must attribute primary-handler / creator duties to #3.
5. **#1 Philon is a multi-level scoring forward, NOT a traditional PF.** Pops to elbow on BLOBs, hits 3s, drives, scores inside. Don't characterize as a "rim-running big." 3-level scorer is the right framing.
6. **#42 Daniels is the screen-and-roll engine.** Primary PnR screener, DHO partner in Horns, lob target, post-finisher, "very strong." Cannot be a generic "rim-runner big" — his connector role in PnR + Horns is the key insight.
7. **#11 Delancy is the late-clock 1-on-1 creator (paired playmaker with #3).** Q4 1:35 explicit "play maker too like #3." Critical late-game scouting note.
8. **#2 Miller is the secondary PnR handler and late-game closer.** Handled the PnR on key Q4 possessions (Q4 4:51 kick-out to #1 for 3, Q4 2:42 drive for FT, Q4 0:39 PnR TO). Not a pure off-ball receiver.
9. **Pressure man-to-man is the base defense, NOT a press team.** Only ONE 1-2-1-1 press deployment in the entire film (Q1 0:57). TEX should NOT characterize Montverde as a press team. Press is `[SINGLE GAME SIGNAL]` situational.
10. **The critical defensive weakness is "cannot guard Brewster #0" in the late-game stretch.** This is THE actionable opposing-scout tip from this film. Whoever Montverde assigned (likely #3) couldn't contain him. `[CONFIRMED]`.
11. **PnR coverage is `[NOT OBSERVED]` in chunks 1, 2, 3.** Only 2 logged PnR-defense possessions in the entire film (both chunk 0, both drop). TEX outputs that confidently characterize Montverde as a "drop team" are over-extending from a 2-possession sample. Drop is `[LIKELY]` from chunk 0 only.
12. **Game WAS close late.** Brewster briefly took the lead 68–69 at Q4 2:47, and the Q4 2:00 margin was just 1 point. Final ~14 seconds was Brewster's intentional-foul sequence. Any TEX output that produces "blowout" or "Spire-like Q3 inflection" language is hallucinating. The game was a wire-to-wire control → comeback → survival.
13. **#1 Philon cramped at Q4 1:54 and was subbed out for the final ~90 seconds.** Closing lineup is #3 #2 #11 #10 #42. Any close-game tendency claims must reflect this personnel change. TEX should not attribute closing-lineup actions to #1.
14. **No Spain PnR, no Flex (named), no Iverson cut, no Princeton set.** The named inventory is 1-4 flat / High PnR + Horns + 4-out 1-in motion + transition + BLOB family + iso (1x). TEX outputs that label any Montverde set as Spain PnR or Flex are mis-labeling.
15. **Brewster played 1-2-2 zone for parts of Q2–Q3.** Montverde reacted with 2-2-1 / "guards-up" zone offense. These zone-offense possessions are reactive, not base half-court — TEX should flag them separately.

---

## SECTION 11 — HOW THIS DOCUMENT GETS GRADED

When TEX runs against this film, grading walks through each numbered section:

| Section | Graded how |
|---|---|
| 2 — Action inventory | Each action TEX identifies is compared to this list. `captured / missed / hallucinated`. |
| 3 — Tempo | Does TEX's claim match yours within tolerance? |
| 4 — OOB sets | Each OOB TEX identifies compared to yours. |
| 6 — Base scheme | Does TEX identify man-to-man + situational press? |
| 7 — Ball screen coverage | Hedge + blitz + switch primary identified? Drop NOT identified (correctly)? |
| 8 — Individual defensive tendencies | Each claim compared to yours. |
| 9 — Player profiles | Each player's handedness, role, tendencies compared to yours. |
| 10 — Synthesis flags | Did TEX flag the same uncertainties? Is TEX over-confident where you were uncertain? |

The per-section scores roll up to a `captured / missed / hallucinated` table for film 03
and get written to `EVAL_SCORES.md`. Section 11 is documentation only — nothing to fill in.

---

*When every blank above is filled in (or explicitly marked "insufficient observation"),
this document is ready. Commit it. Then run TEX against film 03 and the grading UI will
diff TEX's output against this file.*

*Film 03 is step 3 of 5. Films 04–05 repeat this process. At 5 films complete, golden
set initialization is done and Stage 1 of the commercial ladder (per ROADMAP.md) is gated.*
