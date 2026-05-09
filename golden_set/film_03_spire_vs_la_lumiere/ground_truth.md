# Film 03 — Ground Truth (Answer Key)

**Scouted team:** Spire Institute Academy · **Opponent:** La Lumiere School · **Event:** Nike EYBL Scholastic League (2025-26 season)
**Prompt 0B output shape:** this document mirrors the synthesis structure so TEX's output
can be graded section-by-section against what's here.

This is the authoritative answer key for grading TEX against film 03. Synthesized from
`film_watch_notes.md`. The numbers, names, and tendencies below are the ground truth;
TEX's `chunk_synthesis` output is graded line-by-line against this.

> **Rule 1:** every claim attributes to a jersey number + name.
> **Rule 2:** every count is a number, not a range, unless you explicitly flag uncertainty.
> **Rule 3:** every claim has a confidence tag: `[CONFIRMED]` / `[LIKELY]` / `[SINGLE GAME SIGNAL]`.
>   - `[CONFIRMED]` — observed 3+ times across multiple chunks, or 8+ occurrences total
>   - `[LIKELY]` — observed 2 times, or 4–7 occurrences total
>   - `[SINGLE GAME SIGNAL]` — observed once or only in one chunk. Possible tendency. Not confirmed.
> **Rule 4:** if you don't know, write "insufficient observation" — do not guess.

**Context note:** This is high-school prep program play (EYBL Scholastic), NOT 17U AAU
summer (Films 01 / 02). Spire Institute Academy practices year-round; expect more
structured offense than Films 01 / 02 produced. Don't force the "no real set offense"
finding here if the film actually shows structure — and in this film, it does.

---

## SECTION 1 — GAME HEADER

| Field | Value |
|---|---|
| Scouted team | Spire Institute Academy |
| Opponent | La Lumiere School |
| Final score | Spire `73` — La Lumiere `81` (margin -8, Spire loss, not close in final 2:00) |
| Winner | La Lumiere School |
| Game format | Four 8-min quarters, EYBL Scholastic / HS prep (32 min regulation) |
| Total offensive possessions by Spire | `67 logged` (chunk totals: 17 / 17 / 20 / 13). High confidence — all four chunk possession tables are dense and complete. |
| Total offensive possessions by opponent | Insufficient observation — La Lumiere possessions were not logged 1-for-1; only noteworthy defensive events and ball-screen coverages were tracked. Rough parity with Spire (~65–70) inferable from score/pace but not traceable to the scratchpad. |
| Score progression | 0–0 (start) → Spire 15–15 (Q1 1:36) → Spire 20–22 (end Q1) → Spire 28–30 (Q2 3:05) → Spire 34–39 (halftime) → Spire 34–42 (Q3 7:29) → Spire 40–42 (Q3 6:21) → Spire 42–52 (Q3 3:17) → Spire 47–57 (Q3 1:25) → Spire 49–59 (end Q3) → Spire 55–66 (Q4 4:36) → Spire 63–73 (Q4 2:33) → Spire 73–81 (final) |
| Game shape | Close, defense-heavy game wire-to-wire. Tied 15–15 mid-Q1; LL led 22–20 after Q1; LL stretched to 5 at half (39–34). Q3 was the inflection — LL pushed lead from 2 to 10 between Q3 6:21 and Q3 3:17, then to double digits the rest of the way. Spire never recovered after the Q3 run; final-2:00 margin was 9–10 pts. **Not a close game late.** |
| Date of game | 2025-26 EYBL Scholastic season (exact date not captured in metadata) |
| Event | Nike EYBL Scholastic League — 2025-26 season |
| Source film | YouTube `406zMmbgC0I` (film_id TBD post-upload) |

---

## SECTION 2 — OFFENSE: SET AND ACTION INVENTORY

**Framing note:** Unlike Films 01 / 02 (BBE / Rebels), Spire Institute Academy DOES run
a structured half-court offense. The dominant action is a repeating motion-offense
sequence: weave / pass-and-cut-through at the top of the key → down-screen for a
guard (`#2 Gibson` or `#0 Bouie`) coming up from the baseline → DHO with the big at
the top of the key → drive or pull-up. This sequence repeats 10+ times across the game
and is unmistakable. Spire is patient, swings the ball side-to-side, and players fill
empty spots rather than standing. **This is a real finding about Spire — they have
genuine half-court structure, materially different from BBE / Rebels.**

*Counts reconcile scratchpad language per §10a. Sorted by total occurrences descending.*

### Action A: Motion / weave + down-screen + DHO ("base motion")

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~25` (breakdown: chunk 0: `~7` (poss 2, 4, 8, 12, 13, 14, 15, 17), chunk 1: `~6` (poss 3, 6, 7, 9, 11, 16), chunk 2: `~10` (poss 1, 2, 3, 4, 6, 7, 8, 13, 17, 18, 19), chunk 3: `~3` (poss 2, 3, 4)).
  - Representative possessions: C0-2 (`Q1 7:34` weave at top → #4 down-screens for #11 → DHO sequence → 3pt miss), C0-4 (`Q1 6:40` `[3pt make]` — #2 baseline cut off #4 screen → DHO with #11 → open 3), C0-13 (`Q1 2:09` weave + back screens → #0 sets back screen + #4 screens for him → 3pt make), C1-3 (`Q2 6:00` back screen → screen-the-screener → #14 layup off pass), C2-1 (`Q3 7:03` `[2pt make]` — #4 screens away for #0 → DHO with #11 → layup), C2-2 (`Q3 6:36` same action no down-screen → #11 DHO with #0 → easy layup), C3-2 (`Q4 3:46` `[2pt make and-1]` — #2 baseline → DHO with #11 → drive + and-1).
- **Primary initiator(s):** `#3 Davis` (primary PG — runs the entry, brings ball up, slows pace before action). `#2 Gibson` (initiates as the receiver coming off the down-screen — primary scoring outlet). `#0 Bouie` (interchangeable with #2 as the cutter / receiver).
- **Primary screener(s):** `#11 Pur` (primary big — sets the down-screen and/or executes the DHO at top of key). `#14 Rinaldo-Komlan` (secondary big — same role when subbed in for #11). `#4 Derkack` (sets the down-screens for guards coming from baseline; also occasional DHO).
- **Typical floor position:** Initiated from top of key (entry pass to elbow / wing). Down-screen happens on the wing or off-baseline; DHO is at the top or top-of-key. Cutter (#2 or #0) ends up with the ball facing the basket, options to drive or pull up.
- **Success rate:** `~14 of ~25 produced points or FT trips`. Multiple makes (C0-4 3pt, C1-3 layup, C2-1 layup, C2-2 layup, C3-2 and-1, C3-3 FT trip). Misses are common but the action consistently produces a clean look.
- **Key counter (if taken away):** When the DHO doesn't yield a drive, ball-handler pulls it back out and Spire either re-runs the same action (C2-19 same shot as C2-18 because it worked) or kicks into a high PnR with #11 (Action B).
- **Reconciliation note:** Per §10a, unified "motion," "DHO," "down-screen DHO," "weave," "pass and cut-through," "screen-the-screener," "back screen + DHO" under this category. They share the same skeleton (perimeter motion → off-ball screen for guard → DHO with big → attack). Naming this **"base motion"** — it is Spire's primary half-court action.
- **Situational use:** Run all four chunks. Increases in Q3 once Spire commits to it as their reliable bucket-getter (10 of 20 Q3 possessions logged this action explicitly). Spire will run it back-to-back if it works (C2-18 / C2-19 — same exact shot in successive possessions, "if it works they will run it right back").

### Action B: High PnR (#3 + #11 / #14, 4-out 1-in)

- **Confidence:** `[CONFIRMED]`
- **Total occurrences:** `~10` (breakdown: chunk 0: `~3` (poss 6, 9, 16), chunk 1: `~3` (poss 13, 14, 17 — typically embedded inside motion), chunk 2: `~2` (poss 12, 15), chunk 3: `~3` (poss 1, 4, 6, 10)).
  - Representative possessions: C0-6 (`Q1 5:37` high PnR → swing left → roll-man #11 open → ball back right → #0 drive + foul → FT trip), C0-9 (`Q1 4:15` 5-out PnR `[3pt miss]` — #3 drive off #11 screen, kicks for swing), C2-15 (`Q4 7:24` off-BLOB PnR → roll-man finish `[2pt make]`), C3-1 (`Q4 4:08` PnR → #0 drive `[FT 1-of-2]`), C3-6 (`Q4 2:14` PnR `[3pt make]` — #3 off #11 screen, kicks to #0 corner).
- **Primary initiator(s):** `#3 Davis` (primary handler in PnR — `~7 of 10`). `#0 Bouie` (secondary — operates the PnR when #3 has swung the ball off).
- **Primary screener(s):** `#11 Pur` (primary — `~8 of 10` PnRs are with #11). `#14 Rinaldo-Komlan` (when subbed in).
- **Typical floor position:** Top-of-key or strong-side wing PnR. 4-out 1-in spacing. Ball-handler attacks off the screen, kicks if defense collapses, sometimes hits the roll-man.
- **Success rate:** `~5 of ~10 produced a good look that scored or drew a foul` (C0-6 FT trip, C2-15 roll finish, C3-1 FT, C3-6 kick-out 3pt make). Roughly 50% efficiency — comparable to the base motion, used as a relief-valve when motion stalls.
- **Key counter (if taken away):** Decline + iso (rare for Spire) or re-run the base motion (Action A).
- **Reconciliation note:** Unified "PnR," "high PnR," "4 out 1 in PnR," "5 out PnR," "PnR and DHO" under this category. The 4-out / 5-out spacing detail is real but the action is structurally the same.
- **Situational use:** Increases late in possessions when motion doesn't yield a shot. Used heavily in Q4 (3+ in chunk 3 alone). Comfortable scoring action but less frequent than base motion.

### Action C: Iso / 1-on-1 attack

- **Confidence:** `[LIKELY]`
- **Total occurrences:** `~5` (breakdown: chunk 0: `~2` (poss 1, 5), chunk 1: `~3` (poss 1, 5, 12), chunk 2: `~1` (poss 5 — turnover), chunk 3: `0`).
  - Representative possessions: C0-1 (`Q1 8:00` `[2pt miss]` — #2 cuts to basket off tip, missed layup), C0-5 (`Q1 6:01` `[2pt miss]` — #4 forces drive on 2-3 defenders), C1-1 (`Q2 6:36` `[3pt miss]` — #3 takes defender 1-on-1, drive-and-kick), C1-5 (`Q2 5:13` `[2pt miss]` — #3 takes defender 1-on-1, forced bad shot), C2-5 (`Q3 4:48` `[turnover]` — #3 takes defender 1-on-1, turns it over).
- **Primary initiator(s):** `#3 Davis`, `#2 Gibson`, `#4 Derkack`. Roughly evenly distributed.
- **Success rate:** `~1 of ~5 produced points` — iso is **NOT** a high-efficiency mode for Spire. The team is much better in motion / DHO / PnR than in pure 1-on-1 creation.
- **Reconciliation note:** Spire iso is rare and inefficient. Unlike BBE / Rebels (Films 01 / 02), Spire does not default to iso — they default to motion. Iso emerges when the game speeds up or when a guard reads a mismatch.
- **Situational use:** Scattered — no clear pattern. More common when Spire pushes in early offense before setting up half-court.

### Action D: Transition / push

- **Confidence:** `[LIKELY]`
- **Total occurrences:** `~6 opportunities / ~3 scores` (breakdown: chunk 0: `0 opps / 0 scores`, chunk 1: `~4 / ~2` (poss 4, 8, 10, 15), chunk 2: `0`, chunk 3: `~2 / ~1` (poss 8, 11)).
  - Representative possessions: C1-4 (`Q2 5:37` `[2pt make]` — #0 coast-to-coast off rebound), C1-8 (`Q2 3:47` `[FT 2-of-2]` — half-court trap → #3 steal → drive + foul), C1-10 (`Q2 2:52` `[2pt make]` — #2 pushes, dumps to #11 for layup), C1-15 (`Q2 0:05` `[FT 2-of-2]` — #3 length-of-court steal → pass to #11 fouled), C3-8 (`Q4 1:13` `[2pt make]` — #0 steals → kick to #3 → baseline layup), C3-11 (`Q4 0:29` `[3pt FT 3-of-3]` — #3 steal → pass to #2 fouled on 3pt attempt).
- **Primary initiator(s):** `#3 Davis` (steals → push), `#0 Bouie` (rebound → push), `#2 Gibson` (occasional push).
- **Success rate:** `~3 of ~6 produced points`. Roughly 50% conversion when the opportunity arises.
- **Reconciliation note:** Spire is **NOT** a transition team. Pace feel is "slow halfcourt pace" across all 4 chunks per scratchpad. Transition is opportunistic, not a base mode. Most transition opportunities come from steals (especially out of full-court / half-court traps), not from defensive rebounds + pushes.
- **Situational use:** Q4 transition picks up because Spire is trailing and pressing. Out-of-trap steals → fast break is the most consistent transition trigger.

### Action E: Post-up / 4-out 1-in feed (#14 / #11)

- **Confidence:** `[LIKELY]`
- **Total occurrences:** `~3` (chunk 2: poss 10, 11; chunk 0: poss 2 (`#11 sealed off man really well in post`)).
  - C2-10 (`Q3 2:08` `[2pt make]` — #14 post-up + score after motion), C2-11 (`Q3 1:39` `[turnover]` — #14 fed in post, can't score, turned over).
- **Primary target:** `#14 Rinaldo-Komlan` (when in game), `#11 Pur` (when posting).
- **Success rate:** `1 of ~3 — 1 score, 1 TO, 1 setup`. Inconsistent. Bigs can establish position when sealing off OREB chases (C0-2) but struggle when fed cold from the perimeter (C2-11).
- **Reconciliation note:** Posting up is NOT a primary scoring action for Spire. It's a relief option late in the shot clock or when a big establishes position via OREB chase.
- **Situational use:** Late-Q3 burst when #14 was on the floor. Two consecutive possessions tried to feed him — second one turned over.

### Action F: Elevator / staggered screens for shooter

- **Confidence:** `[SINGLE GAME SIGNAL]`
- **Total occurrences:** `2` (chunk 2 poss 16 `Q4 6:50` — elevator screen for #12 3pt miss; chunk 3 poss 7 `Q4 1:28` — elevator screen, #0 pops to left wing → 3pt airball miss).
- **Structural description:** Two screeners (typically #4 and #11) form an elevator (parallel screens) at the elbow. Shooter cuts from baseline up through the elevator and pops to the wing for a catch-and-shoot.
- **Reconciliation note:** Real designed structure but small sample. If film 04 / 05 shows it again, upgrade to `[LIKELY]`.

### Single-occurrence / variant actions (one-line each, listed for completeness)

*Not part of the repeating inventory but observed:*

- `C0-3 Q1 7:19` — Pure offensive rebound conversion: #11 boards his own teammate's miss → finishes layup.
- `C0-7 Q1 5:12` — Quick C&S off advance pass — #4 transition catch-and-shoot 3pt miss.
- `C0-10 Q1 3:47` — Quick inbound after make → 1-pass advance to #0 → quick 3pt make.
- `C0-11 Q1 3:22` — Pure hesi drive iso — #2 hesitation drive for layup. Variant of Action C.
- `C2-14 Q4 8:00` — BLOB Box — see §4.
- `C3-12 Q4 0:13` — Dribble pull-up by #3 → miss → #0 tip-dunk OREB conversion. Late-game broken-play.
- `C3-13 Q4 0:03` — Last-possession heave 3pt by #2.

**Reminder on what's NOT here:** No Horns sets observed. No Spain PnR. No Flex (in the named sense — Spire's motion is screen-the-screener, not Flex). No Iverson cut. The named inventory is base motion + PnR + 4-out 1-in feed + transition + elevator. TEX outputs that produce "Horns," "Spain PnR," or "Flex" terminology from this film are hallucinating.

---

## SECTION 3 — OFFENSE: TEMPO AND PACE

- **Primary tempo:** `slow halfcourt` — Spire deliberately runs their motion offense; players are patient, ball swings side-to-side, no one holds the ball too long. Pace feel logged as "slower halfcourt pace" / "slow halfcourt pace" / "mostly half court offense game" across chunks 0, 1, 2. `[CONFIRMED]`
  - **Frequency evidence:** ~6 transition opportunities logged across 67 possessions (~9% of possessions are transition). Compare to Film 01 BBE which had ~16 of 57 (~28%) — Spire is materially slower / more set-oriented.
  - Typical transition triggers: half-court / full-court trap → steal → fast break (C1-8, C1-15, C3-8, C3-11). Defensive rebound + outlet is rare; #3 explicitly slowed the ball after a #2 rebound at Q3 6:36 ("could've pushed but slows ball down to run offense — #3 smart PG").
- **Average time to half-court action initiation:** `moderate to deliberate` (8–14s). Spire enters into base motion (Action A) on most possessions — initial pass to wing or elbow, then weave / cut-through develops over 4–6 seconds before the down-screen + DHO. Rarely under 6 seconds except in transition.
- **Pace changes (situational):**
  - **#3 Davis deliberately slows the game to set up motion** — confirmed at C2-2 (`Q3 6:36` "could've pushed but slows ball down to run offense — #3 smart PG"). `[CONFIRMED]`
  - **Q4 pace accelerates when Spire is trailing** — full-court press defense by LL forces Spire into more transition / iso / quick-shot mode. Multiple Q4 possessions ended with quick 3pt attempts (C3-7, C3-9, C3-10, C3-13). `[CONFIRMED]`
  - **Spire will re-run a successful action immediately** — explicit at C2-18 / C2-19 ("If it works they will run it right back"). Pace doesn't reset between possessions on the run-back. `[LIKELY]`
- **Confidence on tempo claims:** `[CONFIRMED]` overall. The "slow halfcourt with motion" finding is well-supported across all 4 chunks; the transition rate is `[LIKELY]` because LL pace dragged the game.

---

## SECTION 4 — OFFENSE: OUT-OF-BOUNDS SETS

*BLOB = baseline out-of-bounds. SLOB = sideline out-of-bounds.*

### BLOB #1: Box formation — screener-pop or cross-cut

- **Confidence:** `[LIKELY]`
- **Total occurrences:** `2` (`Q2 1:54` chunk 1, `Q4 7:24` chunk 2).
  - `Q2 1:54` — Box formation (2 elbow / 2 block). Top man on ball-side faked a screen to opposite elbow; opposite-side block player went up to set the screen. Nothing was open. Spire bailed by inbounding to half-court. Outcome: `[2pt miss]` on follow-up offense.
  - `Q4 7:24` — Box formation. Screener for elbow → elbow player pops to corner → catches inbound. Successfully inbounded; flowed directly into PnR (poss 15, see §2 Action B) → roll-man finish for `[2pt make]`.
- **Primary target (who's supposed to score):** Elbow popper / corner shooter (typically `#2 Gibson` based on the Q4 7:24 lineup). Not designed for an immediate shot — designed to safely inbound and flow into half-court action.
- **Screeners:** Block players (#11, #14, or #4 depending on lineup). Screen-the-screener variant on Q2 1:54.
- **Structural description:** Box set baseline alignment. Inbounder under basket. 2 players on elbows, 2 on blocks. Designed first option is a fake-screen + real-screen for an elbow popper to pop to a corner or wing; secondary option is a cross-cut for a guard. Rarely produces an immediate shot — typically a safe inbound + flow.
- **Success rate:** `1 of 2 produced a successful inbound that led to a score` (Q4 7:24 → PnR roll finish). The other was an inbound to half-court for a reset.
- **Reconciliation note:** Spire's BLOB is **flow-into-offense**, not a designed shot generator. Both occurrences used the same Box formation as the starting alignment.
- **Situational use:** Both occurrences after timeouts / late in periods when Spire wanted to ensure a clean inbound rather than force a quick look.

### SLOB sets

- **Total occurrences observed:** `0` cleanly logged. Insufficient observation — no SLOB rows in any chunk's special-situations table.
- **Confidence:** `[NOT OBSERVED]`.

### ATO sets

- **Total occurrences observed:** `0` cleanly tagged as ATO in the scratchpad. The Q4 7:24 BLOB followed a stoppage but isn't tagged ATO specifically.
- **Confidence:** `[NOT OBSERVED]`.

### Late-clock / end-of-period plays

- **C0-16 `Q1 0:08`** — End-of-Q1: PnR + DHO sequence, defended well, swung opposite side, #4 DHO shot 3pt miss at buzzer. No specific designed end-of-period set; a flow possession that ran out of clock.
- **C3-13 `Q4 0:03`** — End-of-game: #2 dribbles up, takes 3pt heave, miss. Pure desperation.

*Noting: Spire ran NO repeating designed end-of-period sets in this film. End-of-period possessions devolved into either re-running base motion or quick iso. `[CONFIRMED]` no end-of-period set inventory.*

---

## SECTION 5 — OFFENSE: LATE-GAME (final 8 minutes of close games)

- **Close late?** `NO` — at the 2:00 mark of Q4, Spire trailed 63–73 (-10). Final margin -8. Game was effectively decided by ~Q4 4:00 when LL's lead reached 11 and never narrowed. Final 2:00 was outside the 6-pt close-game window.
- **Late-game tendencies — GAME NOT CLOSE.** Per grading discipline, what Spire DID run in the final 2:00 is captured here for contrast — with explicit caveat that **these are catch-up / pressing-trail behaviors, not close-game execution.**

### What Spire actually ran in the final 2:00 (catch-up mode, NOT close-game execution)

- **Primary mode: quick-shot 3s + steal-and-go transition off LL's late ball-handling.** No half-court sets called late. Spire pressed full-court, generated steals, and pushed for quick scores.
- **Possession breakdown for the final 2:00** (chunk 3 poss 7–13, `Q4 1:28 → Q4 0:03`):
  - `Q4 1:28` — Elevator screen for #0 popping to left wing → 3pt airball miss. Designed catch-up shot.
  - `Q4 1:13` — `[2pt make]` Steal off full-court press by #0 → drive + kick to #3 → baseline layup. **Pure catch-up transition.**
  - `Q4 0:45` — `[3pt miss]` 5-out, #4 takes quick advance shot under 1:00.
  - `Q4 0:36` — `[3pt miss]` PnR with #11 → #3 pulls up for 3 instead of using screen.
  - `Q4 0:29` — `[FT 3-of-3]` Steal by #3 → pass to #2 → fouled on 3pt attempt. **Best execution of the catch-up sequence.**
  - `Q4 0:13` — `[OREB → 2pt make tip dunk]` #3 pulls up, miss, #0 tip-dunk.
  - `Q4 0:03` — `[3pt miss]` Final possession, #2 dribbles up, heave, miss.
- **Primary ball-handler in catch-up:** `#3 Davis` — primary press-stealer + scorer in late mode. `#2 Gibson` and `#0 Bouie` rotated as receivers / shooters off steals.
- **Primary scorer / foul-drawer when a bucket is needed:** `#2 Gibson` (pulled-up 3pt fouled, FT 3-of-3 at Q4 0:29). `#3 Davis` (steal-and-go layups).
- **Primary rebounder / put-back:** `#0 Bouie` (tip-dunk Q4 0:13, OREB conversion in catch-up sequence).

### What IS observable about late-game execution (game not close, take with caution)

- **Shot clock offense (under 8 seconds):** Insufficient observation at normal end-of-close-game state. Related data point: when motion stalls, Spire defaults to PnR with #11 — observed C0-16 (end-of-Q1 PnR → DHO buzzer 3pt miss). `[SINGLE GAME SIGNAL]`.
- **Scheme changes when trailing:** `YES, defensively.` Spire ramped pressure throughout Q3–Q4 — full-court traps with #11 at the top, half-court traps, deliberate steal attempts. This is a trailing-team scheme, not a base posture. `[CONFIRMED]`
- **Scheme changes when protecting lead:** Insufficient observation — Spire never had a meaningful lead to protect. `[NOT OBSERVED]`
- **Confidence on late-game tendencies:** The *trailing-game* late-game mode is `[CONFIRMED]` (press → steals → quick shots, no plays drawn up). The *close-game* late-game mode is `[NOT OBSERVED]` and should be flagged in the grading rubric — any TEX output that makes confident close-game-late claims from film 03 is hallucinating.

---

## SECTION 6 — DEFENSE: BASE SCHEME

- **Primary defense:** `man-to-man` — Spire ran tough man-to-man as the base for nearly the entire game. Aggressive ball pressure, denial off-ball, active help. Layered on top: situational full-court press / half-court traps that returned to man-to-man after the trap broke down. `[CONFIRMED]`
- **Percentage of possessions (approximate):** Man-to-man `~85%` / press-or-trap `~15%`. The press / trap layers are situational (after Spire scores, late in quarters when trailing), not the base.
- **Scheme posture by quarter:**
  - **Q1 (chunk 0).** Pure man-to-man. Examples: C0 def `Q1 6:20` "solid man to man defense, #2 great off-ball denying defender for contested 3pt miss." `Q1 5:23` "great communication off off-ball screens switches, #11 great switch and contest." Notable Q1 deployment: `Q1 1:47` Spire double-teamed the ball-handler in the BACK COURT after a 3pt make, then dropped back into man-to-man. **First press appearance.**
  - **Q2 (chunk 1).** Mostly man-to-man. New look: `Q2 3:43` "looks like some sort of zone press with #11 at the top" → fell back into man. Half-court trap deployments at `Q2 0:17` (steal) and `Q2 0:51` (double off ball-screen — left LL roller wide open).
  - **Q3 (chunk 2).** Man-to-man with increasing press deployment. `Q3 7:18` "press with #11 at top, trapping at half-court — they trap right when you cross half-court, pass ahead before half-court, #11 is tall and long and at top — hard to pass over." `Q3 2:22` full-court man-to-man press → #3 gets beaten coast-to-coast for a dunk.
  - **Q4 (chunk 3).** Heavy press deployment. `Q4 4:22` full-court pressure with trap. `Q4 4:00` full-court press w/ trap broken by LL alley-oop dunk. `Q4 5:13` full-court press into trap → foul. **Press is the base scheme posture in Q4 because Spire is trailing.**
- **Pressure level:**
  - In man (all quarters): `pressure` — strong on-ball, denial off-ball, communication on screens. Multiple "solid man to man" / "tough man to man defense" notes.
  - In press / trap: `pressure` — `#11 Pur` is the trap-trigger (top of press, traps ball-handler at half-court). Generates steals (C1-8 trap → steal, C1-15 length-of-court steal, C2 def `Q3 7:18`). Also generates breakdowns (C2 def `Q3 2:22` coast-to-coast dunk, C3 def `Q4 4:00` alley-oop dunk).
- **Off-ball positioning:**
  - In man: `deny / gap` — active denial. C0 def `Q1 6:20` #2 actively denying his man on off-ball. `Q1 3:37` "players are in good help position." `Q1 5:23` great communication on off-ball screen switches.
- **Post defense:** `[LIKELY]` aggressive — bigs (especially #11) hedge / show / switch on screens involving the post. No specific post-front observations logged.
- **Transition defense:** **Inconsistent — explicit weakness when Spire misses or turns it over.**
  - `Q1 5:48` "transition defense — off bad miss Spire did not get back, 3-on-2, drive-kick to open LL man for 3pt make."
  - `Q1 5:05` "transition defense after bad shot — did not stop ball-handler, LL goes coast-to-coast for and-1 layup. Bad defense by Spire."
  - `Q3 2:22` full-court press collapse — LL beat one ball-handler coast-to-coast for dunk.
  - `Q4 4:00` press break → alley-oop dunk.
  - **Pattern: Spire either presses successfully or gets beaten badly in transition. Limited middle ground.** `[CONFIRMED]`
- **Drive-and-kick weakness:** **The single most exploitable team defensive tendency.** Multiple scratchpad notes:
  - `Q3 3:28` "solid defense but drive and kick beat Spire for open 3."
  - Whole-game wrap-up: "Spire lets up a lot of drive-and-kicks, and LL just hit the shots."
  - **Causes:** Help defenders rotate to ball, leaving shooters open on the perimeter. Closeouts arrive late on the kick-out shooter. `[CONFIRMED]` — biggest game-level weakness.
- **Confidence:** `[CONFIRMED]` for man-to-man as base. `[CONFIRMED]` for press / trap as situational layer with #11 as the trap-trigger. `[CONFIRMED]` for drive-and-kick as the primary exposure. `[LIKELY]` for exact press-vs-man split.

---

## SECTION 7 — DEFENSE: BALL SCREEN COVERAGE

- **Primary coverage:** `hedge` and `double / blitz` (both prevalent) — with `switch` as a secondary option. Spire is **not** a drop-coverage team; they are aggressive on ball screens. `[CONFIRMED]`
- **Frequency (of 8 logged PnR defensive possessions across chunks 0–1):**
  - `hedge` — **2 of 8** (C0 `Q1 (no timestamp)` 3pt miss, C0 `Q1 (no timestamp)` 2pt miss). Both with `#11 Pur` as screen defender.
  - `double / blitz` — **3 of 8** (C0 `Q2 7:50` `[2pt miss]`, C0 `Q2 7:26` `[2pt miss]`, C1 `Q2 0:51` `[2pt make]` — roller wide open).
  - `switch` — **3 of 8** (C0 `Q1 0:23` 2pt mid-jumper, C1 `Q2 6:28` defensive foul on #14, C1 `Q2 2:21` 2 PnR switches no score).
  - No `drop`, `ICE`, or `show` coverages observed.
- **Coverage timeline (did it change during game?):**
  - **Q1:** Hedge primary. #11 hedges + recovers cleanly twice (`Q1 (no timestamp)` 3pt miss, then `Q1 (no timestamp)` 2pt miss with hand-off recovery to roller).
  - **Q2 (early):** Double-team / blitz becomes the dominant coverage. Spire double-teamed ball-handler twice in succession at `Q2 7:50` and `Q2 7:26` — both produced misses. **First clear shift in coverage philosophy.**
  - **Q2 (mid-late):** Switch becomes more common (C1 `Q2 6:28`, `Q2 2:21`). One blitz at `Q2 0:51` left the roller wide open in the middle of the paint for a make — clear breakdown.
  - **Q3–Q4:** No PnR defense rows logged in chunks 2 / 3. LL ran fewer traditional ball screens late (Spire was pressing full-court, so LL spent more time breaking pressure than running PnR). PnR defense inventory effectively drops off the board after Q2.
- **Coverage by personnel:**
  - **#11 Pur** is the screen defender in `~6 of 8` logged PnR possessions. He is the primary big in PnR coverage when on the floor.
  - **#14 Rinaldo-Komlan** was screen defender on `~3 of 8` PnRs (C0 `Q1 0:23` switch, C1 `Q2 6:28` switch + foul). Subbed in for #11 multiple times during game.
  - **#4 Derkack** was screen defender on `Q2 2:21` (switches).
  - Ball defender was usually `#3 Davis` (4 of 8) or `#2 Gibson` (3 of 8). Very guard-heavy ball-defense distribution.
- **Execution quality (where does it break down?):**
  - **Blitz coverages can leave the roller wide open** — `Q2 0:51` is the explicit breakdown ("double off ball screen — left LL roll man wide open. No help"). When the help defender doesn't rotate to the roller, blitz turns into a 4-on-3 against Spire's defense.
  - **Hedges are well-executed by #11** — both Q1 hedges produced misses, and #11 successfully recovered to his man / rotated to the roller in both cases.
  - **Switches with #14 produced fouls** — `Q2 6:28` switch on PnR led to #14 fouling the ball-handler. `[SINGLE GAME SIGNAL]`.
  - **Overall breakdown rate:** `~3 of 8 logged PnR possessions` resulted in a Spire-negative outcome (score allowed, foul, or open look). Roughly 60% positive — better than Film 01's BBE PnR defense (~50% positive), with the caveat of a smaller sample.
- **Confidence:** `[CONFIRMED]` for hedge + blitz / double as primary, switch as secondary. `[CONFIRMED]` for #11 as primary screen defender. `[LIKELY]` for the exact coverage percentages given the small PnR sample (8 possessions). `[CONFIRMED]` that Spire is NOT a drop team — no drop coverage observed.

---

## SECTION 8 — DEFENSE: INDIVIDUAL DEFENSIVE TENDENCIES

*One block per Spire player with significant defensive minutes. Most starters appeared in all 4 chunks; rotation pattern in `film_watch_notes.md` gives rough denominators.*

### #3 — Darrell Davis (PG, 5'11", Jr 2027)

- **Primary defensive assignment:** LL's primary ball-handler when in man; pressures full-court at times; ball-defender on PnR (4 of 8 logged).
- **On-ball quality:** `[CONFIRMED]` **strong.** C1 def `Q2 3:56` "#3 guards ball full-court — once LL comes to half-court they double the ball-handler. #3 comes with a steal." Multiple pressure-based steals: C1-8 (Q2 3:47 steal → FT trip), C1-15 (Q2 0:05 length-of-court steal), C3-11 (Q4 0:29 steal).
- **Help activity:** `active` — pressures inbound, attacks ball-handler off the dribble, generates trap steals.
- **Identified weakness:** Got beaten coast-to-coast on full-court press at `Q3 2:22` (LL ball-handler "went coast to coast and dunked it"). When the trap doesn't form, #3's individual size at 5'11" can be exploited by a bigger handler. `[SINGLE GAME SIGNAL]`.
- **Confidence:** `[CONFIRMED]` strong on-ball pressure / steal generation. `[SINGLE GAME SIGNAL]` size exposure on coast-to-coast.

### #2 — King Gibson (PG, 6'4", Jr 2027)

- **Primary defensive assignment:** LL secondary handler / off-ball wing in man. Off-ball denial role.
- **On-ball quality:** `[LIKELY]` **above average.** Limited specific on-ball observations.
- **Help activity:** `[CONFIRMED]` **strong off-ball denial.** C0 def `Q1 6:20` "#2 shows great off-ball defense playing in help position denying his defender for a pass — held defender to contested 3pt shot miss." Featured in good defensive possessions multiple times.
- **Identified weakness:** None specifically logged. `[NOT OBSERVED]` on individual breakdowns.
- **Confidence:** `[LIKELY]` for above-average defense based on off-ball denial pattern.

### #11 — Charles Pur (C, 6'9", Jr 2027) — **the press / PnR anchor**

- **Primary defensive assignment:** Primary PnR screen defender (6 of 8 logged). Top of full-court press / half-court trap. Rim protector. Versatile — switches onto smaller players.
- **On-ball quality:** `[CONFIRMED]` **strong.** Hedge execution clean (both Q1 hedges produced misses). Switching versatility — C0 def `Q1 5:23` "#11 great switch and contest, #11 seems versatile on defense — can guard different positions."
- **Help activity:** `[CONFIRMED]` **active.** Recovers to roll-man after hedges. Trap-trigger at top of press (`Q3 7:18` "hard to pass over — #11 is tall and long and at top"). Multiple trap-steals attributable to #11's positioning.
- **Identified weaknesses:**
  - **Over-played in press / trap:** C2 def `Q3 6:24` "tough man-to-man defense lots of pressure, trapping corners — #11 over-played on defense and got scored on. But solid man-to-man no help when #11 got beat." Aggressive pressure can lead to over-commits.
  - **Blitz coverage left roller open:** C1 def `Q2 0:51` — when #11 doubled off the screen, no rotation to the roller → wide-open paint score. **Coverage breakdown, not pure individual error, but #11 was the front of the blitz.**
- **Confidence:** `[CONFIRMED]` strong overall PnR anchor. `[CONFIRMED]` versatile switching. `[LIKELY]` over-aggressive in press leading to occasional breakdowns.

### #4 — Aiden Derkack (SF, 6'6", Sr 2026)

- **Primary defensive assignment:** Wing in man. Half-court trap participant (with #0 in C0 `Q1 1:47`). Occasional PnR ball-defender / screen defender.
- **On-ball quality:** `[LIKELY]` **average.** C0 def `Q1 3:37` "#4 was caught sleeping and was back-doored. But #11 rotated perfectly and stopped ball" — back-cut breakdown.
- **Help activity:** `active` on traps — paired with #0 for half-court trap on Q1 1:47.
- **Identified weakness:** **Vulnerable to back cuts** — caught flat-footed at `Q1 3:37`. `[SINGLE GAME SIGNAL]`.
- **Confidence:** `[LIKELY]` average defense overall.

### #0 — Tarris Bouie III (SF, 6'5", Sr 2026)

- **Primary defensive assignment:** Wing in man. Half-court trap participant. Secondary press defender.
- **On-ball quality:** `[LIKELY]` **average to above average.** Generated full-court-press steal at `Q4 1:13` (chunk 3 poss 8: "#0 steals ball off full-court press, drives, and kicks to #3 who then drives baseline and makes a layup").
- **Help activity:** `active` on traps and presses. Occasional steal generator.
- **Identified weakness:** None specifically called out. `[NOT OBSERVED]` for breakdowns attributable to #0.
- **Confidence:** `[LIKELY]` for average-to-above-average defense.

### #14 — Dorian Rinaldo-Komlan (PF, 6'10", Sr 2026)

- **Primary defensive assignment:** Backup big behind #11. Switches on PnR (3 of 8 logged switch coverages were #14). Post defender.
- **On-ball quality:** `[LIKELY]` **inconsistent.** C1 def `Q2 6:28` switched to ball-handler on PnR and **fouled him.** Switching onto guards is exploitable.
- **Help activity:** Limited specific observations beyond switch coverages.
- **Identified weakness:** **Switches onto guards lead to fouls** — `[SINGLE GAME SIGNAL]` from one Q2 6:28 instance, but this is the exploitable matchup if LL targets him.
- **Confidence:** `[LIKELY]` inconsistent on switches.

### Summary — team-level defensive tendencies

- **Drive-and-kick gives up open 3s.** This is the single most actionable defensive scouting tip from film 03. Help rotates to the ball, leaving the kick-out shooter wide open. `[CONFIRMED]` — explicit whole-game observation.
- **Press / trap is high-variance.** When it works, Spire generates steals → transition. When it breaks down, LL gets dunks / and-1s coast-to-coast. `[CONFIRMED]`
- **Spire is a switching + hedging team, NOT a drop team.** Bigs (#11, #14) actively engage at the screen. Opposing bigs who can pop / shoot off pick-and-pop have not been tested in this film. `[CONFIRMED]`
- **Transition defense is weak when Spire turns it over or misses badly.** Three coast-to-coast scores allowed in the film (Q1 5:05, Q3 2:22, Q4 4:00). `[CONFIRMED]`

---

## SECTION 9 — INDIVIDUAL PLAYER CONSOLIDATED PROFILES

*One block per Spire player with 10+ observed offensive possessions. Foundation for the
"Player Pages" section of the final report.*

### #3 — Darrell Davis (seeded PG, 5'11", Jr 2027) — **the real PG**

- **Total possessions observed:** `~50` (breakdown by chunk: ~12 / ~14 / ~14 / ~10). Played the highest minutes — primary handler nearly wire-to-wire.
- **Confirmed position from film:** `PG` — primary ball-handler confirmed.
- **Confirmed dominant hand from film:** `RIGHT` (default — no left-hand observations recorded; multiple pull-up attempts off the dribble all proceeded as if right-handed). `[LIKELY]`.
- **Confirmed role:** `primary_initiator` / `floor general`.
- **Offensive role (specific):** De-facto PG. Brings ball up nearly every possession. Initiates the base motion (Action A) — runs the entry, calls out the action, slows the ball when needed. Patient. **Smart PG** — explicit scratchpad note at C2-2 "could've pushed but slows ball down to run offense — #3 smart PG." Operates as the trigger for high PnR with #11. Hits 3s when motion produces a kick-out.
- **Scoring zones with frequency:**
  - Rim: `~1 of ~3` — direct rim attempts limited. Mostly drives that kick out or end in fouls.
  - Paint (non-rim): `0 of 0`.
  - Mid-range: `0 of 0`.
  - 3pt: `~2 of ~5` — `Q1 3:47` quick C&S 3pt make (advance pass), `Q4 2:14` PnR kick-out 3pt make (poss C3-6, but actual shooter was #0). Misses: C2-13 (open 3), C3-4 (PnR 3 miss), C3-10 (3pt miss).
  - FT attempts: `~3+ trips` (C1-8 Q2 3:47 FT 2-of-2 from steal, C2-8 Q3 3:12 FT 1-of-2, C2-9 Q3 2:42 FT 2-of-2 over-limit, C3-1 Q4 4:08 FT 1-of-2, C3-3 Q4 3:15 FT 1-of-2 — wait, some attributed to others; cleaning up — `~4 clean trips`).
- **Shot chart location summary:** Low-volume scorer overall. Will hit a 3 when the motion produces it. Drives are typically pass-first, foul-drawing.
- **Key tendencies (each tagged with confidence + count):**
  - **Slows the ball deliberately to run offense** `[CONFIRMED]` (explicit C2-2; pace pattern across all 4 chunks).
  - **Primary initiator of base motion (Action A)** `[CONFIRMED]` — initiates the motion sequence on the majority of half-court possessions across all 4 chunks.
  - **Generates steals → transition** `[CONFIRMED]` (C1-8, C1-15, C3-11 — three clean steal-to-FT-or-make sequences).
  - **Pulled-up off PnR for 3 instead of using screen** `[SINGLE GAME SIGNAL]` (C3-10 Q4 0:36 — late-game pulled up early).
- **Defensive assignment:** Primary on-ball defender for LL's PG. Top of full-court press.
- **Defensive vulnerability:** Beaten coast-to-coast on press at `Q3 2:22` for dunk. Size (5'11") is exploitable when trap doesn't form.
- **Free throw shooting observed:** ~4 clean trips, makes per-trip not separated.
- **Turnovers:** `~2` clean attributable (C2-5 1-on-1 turnover, C2-12 PnR fumbled pass to #14).
- **Notable plays (timestamps for the grading UI):**
  - `C1 · Q2 3:47` — half-court trap → steal → drive + foul → FT 2-of-2.
  - `C2 · Q3 6:36` — slowed ball deliberately after rebound, ran motion ("smart PG").
  - `C3 · Q4 0:29` — full-court steal → pass to #2 → 3pt foul → FT 3-of-3.
  - `C0 · Q1 3:47` — quick advance C&S 3pt make.

### #2 — King Gibson (seeded PG, 6'4", Jr 2027) — **the primary scoring guard**

- **Total possessions observed:** `~50` (breakdown: ~14 / ~14 / ~12 / ~10). Played heavy minutes — primary off-ball receiver in motion.
- **Confirmed position from film:** `SG / scoring guard` — **not the primary PG** despite seeded position. Operates as the cutter / shooter / driver receiving the DHO in base motion.
- **Confirmed dominant hand from film:** `RIGHT` — `[CONFIRMED]`. Multiple right-hand drive observations: C1-10 (`Q2 2:52` "really forced a right hand drive — curious to see if he goes left at all"), C0-11 (`Q1 3:22` hesitation drive for layup, right-hand finish), C1-11 (`Q2 2:07` "hard drive to right"). **Explicit scouting tip:** scratchpad flagged "curious to see if he goes left at all" — answer per the rest of the film: he **does not consistently drive left**. `[CONFIRMED]` strong right-hand preference.
- **Confirmed role:** `primary_scorer` / `slasher`.
- **Offensive role (specific):** Primary scoring guard. Comes off down-screens from baseline; receives the DHO at top of key from #11; drives or pulls up. Hesitation-drive specialist (`Q1 3:22` "great one-on-one hesitation drive for a nice layup. Very patient."). High-FT-drawing rate. The **chosen scoring action of base motion is DHO-to-#2-drive.**
- **Scoring zones with frequency:**
  - Rim: `~5 of ~7` — multiple layups: C0-1 (missed off tip), C0-11 (`Q1 3:22` hesi drive layup make), C1-3 (`Q2 6:00` motion layup make), C1-10 (`Q2 2:52` push + dump-off layup make — assist credit), C2-13 (`Q3 0:29` weave + screen → drive layup make), C3-2 (`Q4 3:46` and-1 layup make).
  - Paint (non-rim): `0 of 0`.
  - Mid-range: `~1 of ~2` — C2-18 (`Q4 6:01` open mid-range jumper make — same action), C2-19 (`Q4 5:18` same shot miss).
  - 3pt: `~1 of ~3` — C0-4 (`Q1 6:40` `[3pt make]` open off-DHO 3), C0-7 (`Q1 5:12` C&S 3pt miss), C2-7 (`Q3 3:41` 3pt miss after motion + DHO).
  - FT attempts: `~5+ trips` — C0-6 inferred, C0-12 (`Q1 2:45` FT 1-of-2), C0-14 (`Q1 1:30` and-1 → FT 1-of-1), C3-2 (`Q4 3:46` and-1 → FT 1-of-1), C3-11 (`Q4 0:29` 3pt foul → FT 3-of-3). **High-volume foul-drawer.**
- **Shot chart location summary:** Multi-level scorer. Strong at rim via hesi drives + DHO drives. Mid-range pull-up off motion. 3-point shooter when motion produces a clean look. Heavy right-hand bias on drives.
- **Key tendencies (each tagged with confidence + count):**
  - **Right-hand-dominant drives** `[CONFIRMED]` (3+ explicit observations + scratchpad flag).
  - **Hesitation drive is signature move** `[LIKELY]` (C0-11 explicit; pattern of patient + drive observations).
  - **Primary receiver of DHO in base motion** `[CONFIRMED]` (10+ possessions across all chunks).
  - **And-1 generator on drives** `[LIKELY]` (C0-14 and C3-2 — 2 clean and-1 conversions).
  - **Patient — doesn't rush the action** `[CONFIRMED]` (multiple "very patient" / "doesn't rush" notes across chunks).
- **Defensive assignment:** Wing in man — strong off-ball denial (see §8). Half-court trap participant.
- **Defensive vulnerability:** Not specifically observed. `[NOT OBSERVED]`.
- **Free throw shooting observed:** ~5 trips, makes per-trip varied.
- **Turnovers:** `0 cleanly attributable` in possession logs.
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 6:40` — off-DHO 3pt make (motion poss 4).
  - `C0 · Q1 3:22` — hesitation drive layup.
  - `C0 · Q1 1:30` — and-1 off motion-drive.
  - `C1 · Q2 2:52` — transition drive + dump to #11 for layup (assist).
  - `C3 · Q4 3:46` — and-1 layup off DHO drive.
  - `C3 · Q4 0:29` — 3pt foul → FT 3-of-3 in late-game catch-up.

### #11 — Charles Pur (seeded C, 6'9", Jr 2027) — **the offensive engine**

- **Total possessions observed:** `~48` (breakdown: ~12 / ~11 / ~12 / 13). Heavy minutes; subbed with #14 several times across chunks 0–2. **Played all 13 chunk-3 possessions** (in for the entire final ~4 minutes while Spire pressed trailing).
- **Confirmed position from film:** `C` — true center, primary big.
- **Confirmed dominant hand from film:** **Insufficient observation** — handedness not clearly established on finishes / drives. `[NOT OBSERVED]`.
- **Confirmed role:** `screener` / `connector` / `roller`.
- **Offensive role (specific):** **Hub of base motion.** Pops to top of key, executes DHOs with guards (#2 / #0 primarily), sets the down-screens, sets the high PnR ball-screens, rolls hard, posts up on seals. The motion offense **routes through #11** — he is the connector, not just a finisher.
- **Scoring zones with frequency:**
  - Rim: `~3 of ~4` — C0-3 (`Q1 7:19` OREB layup), C1-7 (`Q2 4:10` OREB tip-back), C2-15 (`Q4 7:24` PnR roll-man finish make), occasional roll-man finishes.
  - Paint (non-rim): `0 of ~1`.
  - Mid-range: `0 of 0`.
  - 3pt: `0 of 0` — does not shoot from deep.
  - FT attempts: `~3+ trips` — C1-15 (`Q2 0:05` FT 2-of-2 transition foul), C2-3 (`Q3 6:05` FT 2/2 from PnR slip), C0-6 (FT trip — possibly inferred).
- **Shot chart location summary:** Rim only. Roller, post-sealer, OREB chaser. **No mid-range or 3pt attempts.**
- **Key tendencies (each tagged with confidence + count):**
  - **Hub of motion / DHO offense** `[CONFIRMED]` (15+ DHO instances across all 4 chunks).
  - **Primary high PnR screener with #3** `[CONFIRMED]` (~8 of ~10 PnRs).
  - **Strong OREB chaser via post-seal** `[CONFIRMED]` — C0-2 ("#11 sealed off man really well in post"), C0-3 (OREB → layup), C1-7 (OREB tip-back). Multiple explicit "great seal" observations.
  - **Slip-screen on PnR — recipient of foul-drawing pass** `[LIKELY]` (C2-3 Q3 6:05 explicit slip → fouled).
- **Defensive assignment:** Primary PnR screen defender, hedger, top of press / trap.
- **Defensive vulnerability:** Over-aggressive in press (Q3 6:24 over-played for score allowed). Blitz coverage breakdown when help doesn't rotate (Q2 0:51).
- **Free throw shooting observed:** ~3 trips.
- **Turnovers:** `0 cleanly attributable`.
- **Notable plays (timestamps for the grading UI):**
  - `C0 · Q1 7:19` — OREB → layup off post-seal.
  - `C1 · Q2 4:10` — OREB tip-back on motion-DHO sequence.
  - `C2 · Q3 6:05` — slip on PnR → drew foul → FT 2-of-2.
  - `C2 · Q4 7:24` — roll-man finish off BLOB-into-PnR.
  - `C0 · Q1 5:23` — defensive switch + contest (versatile defense).

### #4 — Aiden Derkack (seeded SF, 6'6", Sr 2026)

- **Total possessions observed:** `~45` (breakdown: ~14 / ~13 / ~10 / ~8). Heavy minutes; subbed out at Q4 6:03 for #14.
- **Confirmed position from film:** `SF / wing-forward` — operates as a connector wing, not a primary scorer.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `connector` / `screener` / `spot-up shooter`.
- **Offensive role (specific):** Sets down-screens for #2 / #0 in base motion. Occasional DHO partner. Spot-up 3pt shooter when motion swings to him. Occasional iso drive (typically forced and unsuccessful).
- **Scoring zones with frequency:**
  - Rim: `0 of ~1` — C0-5 (`Q1 6:01` forced drive on 2-3 defenders, miss).
  - Paint (non-rim): `0 of 0`.
  - Mid-range: `0 of 0`.
  - 3pt: `0 of ~3` — C0-7 (`Q1 5:12` C&S 3pt miss), C1-2 (`Q2 6:17` C&S 3pt miss), C0-2 (DHO 3pt miss, attribution unclear).
  - FT attempts: `0 cleanly logged for #4`.
- **Shot chart location summary:** Low-volume, low-efficiency in this film. Spot-up 3 attempts missed; iso drive forced.
- **Key tendencies (each tagged with confidence + count):**
  - **Primary screener for #2 in base motion** `[CONFIRMED]` (sets the baseline-up down-screen on multiple motion possessions).
  - **DHO partner secondary to #11** `[LIKELY]` (occasional handoffs when #11 is off-ball or out).
  - **Forced iso drives unsuccessful** `[LIKELY]` (C0-5 explicit "forces drive on 2-3 defenders for bad shot").
- **Defensive assignment:** Wing in man; trap participant.
- **Defensive vulnerability:** Back-cut at `Q1 3:37` (caught flat-footed).
- **Turnovers:** `0 cleanly attributable`.
- **Notable plays:**
  - `C0 · Q1 5:12` — C&S 3pt miss.
  - `C0 · Q1 1:47` — half-court trap participant with #0 (defense).

### #0 — Tarris Bouie III (seeded SF, 6'5", Sr 2026)

- **Total possessions observed:** `~45` (breakdown: ~14 / ~14 / ~10 / ~8). Heavy minutes; subbed out at Q3 0:38 for #12, came back early Q4.
- **Confirmed position from film:** `SF / wing` — secondary cutter / receiver in motion.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `secondary_scorer` / `connector`.
- **Offensive role (specific):** Secondary cutter (alternates with #2 as the down-screen recipient in base motion). Occasional PnR ball-handler. Coast-to-coast finisher in transition. OREB tip-dunk threat late-game.
- **Scoring zones with frequency:**
  - Rim: `~3 of ~4` — C1-4 (`Q2 5:37` coast-to-coast layup make in transition), C2-1 (`Q3 7:03` motion layup make), C2-2 (`Q3 6:36` easy DHO layup make), C3-12 (`Q4 0:13` tip-dunk OREB).
  - Paint (non-rim): `0 of 0`.
  - Mid-range: `0 of 0`.
  - 3pt: `~1 of ~2` — C3-6 (`Q4 2:14` PnR kick-out 3pt make), C3-7 (`Q4 1:28` elevator screen 3pt airball miss).
  - FT attempts: `~2+ trips` — C0-6 attribution (FT 1-of-2 by #0), C3-1 (`Q4 4:08` FT 1-of-2 by #0).
- **Shot chart location summary:** Rim finisher in motion / transition. Spot-up 3 off PnR kick-outs. Tip-dunk threat on OREB chases.
- **Key tendencies (each tagged with confidence + count):**
  - **Coast-to-coast transition finisher** `[LIKELY]` (C1-4 explicit; pattern in late-game steal-to-go).
  - **Cuts hard off motion — receives DHO from #11** `[CONFIRMED]` (multiple motion sequences).
  - **OREB tip-dunk threat** `[SINGLE GAME SIGNAL]` (C3-12 only — but it was a dunk).
  - **Press-break steal generator** `[LIKELY]` (C3-8 Q4 1:13 explicit press steal).
- **Defensive assignment:** Wing in man; press / trap participant.
- **Defensive vulnerability:** Not specifically logged.
- **Free throw shooting observed:** ~2 trips.
- **Turnovers:** `0 cleanly attributable`.
- **Notable plays:**
  - `C1 · Q2 5:37` — coast-to-coast transition layup.
  - `C2 · Q3 6:36` — easy DHO layup off motion.
  - `C3 · Q4 1:13` — full-court press steal → drive + kick to #3 layup.
  - `C3 · Q4 0:13` — OREB tip-dunk.

### #14 — Dorian Rinaldo-Komlan (seeded PF, 6'10", Sr 2026)

- **Total possessions observed:** `~19` (breakdown: ~5 / ~6 / ~8 / 0). Subs in for #11 multiple times; played `Q1 2:35 → Q2 4:10` and `Q3 3:00 → Q4 4:22` per chunk 3 sub log. **Did not appear in any chunk-3 possession personnel row** (subbed out for #4 at Q4 4:22, before chunk 3 begins at Q4 4:24).
- **Confirmed position from film:** `PF / backup C` — operates as the second big when #11 sits.
- **Confirmed dominant hand from film:** **Insufficient observation.** `[NOT OBSERVED]`.
- **Confirmed role:** `screener` / `roller` / `post-up option`.
- **Offensive role (specific):** Backup big in motion + PnR. Post-up option when on the floor (C2-10 post-up score). DHO partner when #11 is off.
- **Scoring zones with frequency:**
  - Rim: `~2 of ~3` — C0-14 (`Q1 1:30` and-1 off motion-drop pass), C0-15 (`Q1 0:56` OREB → and-1 score), C2-10 (`Q3 2:08` post-up score).
  - Paint (non-rim): `0 of 0`.
  - Mid-range: `0 of 0`.
  - 3pt: `0 of 0`.
  - FT attempts: `~2+ trips` — C0-14 (and-1, FT 1-of-1), C0-15 (and-1, FT 0-of-1).
- **Shot chart location summary:** Rim only. Roller, OREB chaser, post-up option.
- **Key tendencies (each tagged with confidence + count):**
  - **Post-up scoring threat when on floor** `[LIKELY]` (C2-10 explicit; C2-11 attempt).
  - **OREB → and-1 finisher** `[SINGLE GAME SIGNAL]` (C0-15 only).
- **Defensive assignment:** Backup PnR screen defender; switches onto guards.
- **Defensive vulnerability:** **Switches onto guards lead to fouls** (C1 def Q2 6:28). `[SINGLE GAME SIGNAL]`.
- **Free throw shooting observed:** ~2 trips.
- **Turnovers:** `~1` (C2-11 — fed in post, can't score, turned over).
- **Notable plays:**
  - `C0 · Q1 1:30` — and-1 off motion-drop pass.
  - `C2 · Q3 2:08` — post-up score.
  - `C2 · Q3 1:39` — post-up turnover.

### #12 — Jalen Parker (seeded PG, 6'4", So 2028)

- **Total possessions observed:** `~5` — limited minutes; entered at `Q3 0:38` for #0 and reappeared in Q4 lineups.
- **Confirmed position from film:** `G / W` — too few possessions to refine.
- **Confirmed role:** `role_player` (limited rotation).
- **Notable involvements:**
  - C2-16 (`Q4 6:50`) — recipient of elevator screen for 3pt miss.
  - C2-14 (`Q4 8:00`) — BLOB receiver in lineup.
- **Confidence:** `[SINGLE GAME SIGNAL]` on tendencies — too small a sample.

### Spire roster — players who DID NOT APPEAR

- **#1 Aiden Dayco-Green, #5 Alex Constanza, #32 Jaylan Mitchell, #55 Nolan Nelson, #93 Collin Ross** — NO possessions observed in any chunk. Either DNPs or garbage-time below observation threshold. Status: `not_evaluated`.
- **#32 Jaylan Mitchell** specifically did not appear despite being on the seeded roster (cross-film flag noted in metadata as same player as Film 01 BBE #32 — but did NOT play in this game).

### Unknown players (seen on film but not on seeded roster)

| # | Short description | Suggested name (if known) | Possessions observed |
|---|---|---|---|
|   | *(none — all 7 observed Spire jerseys (#0, #2, #3, #4, #11, #12, #14) match the seeded roster)* |   |   |

---

## SECTION 10 — SYNTHESIS FLAGS

*Every judgment call you made. Every uncertainty. Every vocabulary reconciliation. Every contradiction resolved. Listing them here is what makes the ground truth honest.*

### 10a — Vocabulary reconciliations

- **"Motion" / "DHO" / "weave" / "pass and cut-through" / "down-screen DHO" / "screen-the-screener" / "back screen + DHO"** were used interchangeably across chunks 0–3 to describe what is structurally the same action: weave at top → down-screen for guard cutting from baseline → DHO with big → drive. Unified in §2 as **"base motion"** (Action A) with total count ~25. Multiple scratchpad notes ("same play as possession X" / "same action again" / "if it works they will run it right back") support this as one repeating action, not many.
- **"PnR" / "high PnR" / "4 out 1 in PnR" / "5 out PnR" / "PnR and DHO"** unified in §2 as **"High PnR with #3 + #11 / #14"** (Action B). The 4-out vs 5-out spacing detail is real but the action is structurally identical.
- **"No set" / "iso" / "1-on-1"** are RARE in this film — unlike Films 01 / 02. Spire has real structure, so iso is logged separately as Action C (5 occurrences) rather than absorbed as "default mode."
- **"Press" / "trap" / "full-court press" / "half-court trap" / "zone press"** describe Spire's situational pressure layer. Unified in §6 as a single scheme ("press / trap with #11 as trigger") layered on top of base man-to-man. The Q2 3:43 "zone press" reference is treated as the same shape as the man-press because Spire fell back into man both ways.
- **"Smart PG" / "patient" / "slows ball" / "doesn't rush"** all describe #3 Davis's tempo control. Unified in §9 as a single tendency: **"Slows the ball deliberately to run offense."**
- **"Drive-and-kick beat Spire"** appears in the Q3 def note AND in the whole-game wrap-up. Unified in §6 / §8 as the team's primary defensive weakness.

### 10b — Counts you are not confident on

- **Per-possession personnel** — chunks 0–3 list 5-jersey lineups for every Spire offensive possession (good discipline). However, many possessions reuse identical lineups, so subtle subs may have been missed.
- **Defensive sequence rows** — only noteworthy events are logged, NOT every LL possession. So the denominator for "Spire defensive efficiency" is unknown; only qualitative observations are valid.
- **Spire team fouls / players in foul trouble** — captured live-tracked fields are mostly empty across all 4 chunks. **Foul-trouble information is NOT reconstructable from this watch notes file.** Any claim about Spire foul trouble in TEX's output should be flagged as not graded.
- **LL forced TOs** — only partially tick-marked (chunk 1: 1, 2; chunk 3: 1, 2). Total Spire-forced LL turnovers is `~4` directionally, not a precise count.
- **OREBs** — chunk totals: 2 / 1 / 0 / 2 = 5 whole-game. Confidence `[CONFIRMED]` on directional claim ("Spire is moderate on OREB"), exact count `[LIKELY]`.
- **FT trips / attempts / makes** — chunk totals: 4/6/3, 3/6/6, 4/8/6, 4/8/6 = 15/28/21 whole-game. Per the watch-notes wrap-up, this matches. `[LIKELY]` on exact, `[CONFIRMED]` on directional.
- **LL transition opportunities / scores** — only chunk 0 logged 2 opps + 1 score. Chunks 1–3 left this field empty or zero. **Likely under-tracked**; LL clearly had transition scores in Q3 (2:22 dunk) and Q4 (4:00 alley-oop). Don't trust the live-tracked tally; trust the defensive-sequence rows.
- **Possession ball-screen coverage in chunks 2 / 3** — both chunks have empty PnR-coverage tables. PnR defense inventory is only directly observable for chunks 0–1 (8 logged possessions). Spire's PnR defense in chunks 2 / 3 is `[NOT OBSERVED]` at the per-possession level.

### 10c — Jersey numbers you could not confirm

- **La Lumiere jersey numbers are mostly unidentified** — scratchpad logs LL events as "LL ball-handler" or "LL #X" without consistent identification. Any individual LL opponent profile is out of scope. The reference roster in metadata is for disambiguation only.
- **Chunk 1 poss 17 — `Q3 7:34`** logged as `FT 2-of-2 (by #3)` — confirmed.
- **Chunk 0 poss 6** logged FT shooter as #0 — that's documented but worth flagging because the listed initiator was #3. Resolved per the scratchpad.
- **Chunk 2 poss 7 — `Q3 3:41`** screener listed as `#11` but personnel includes `#14` (who had subbed in at Q3 3:00). Likely #14 was the screener. Minor inconsistency, flagged.
- **Chunk 3 poss 11 — `Q4 0:29`** outcome `3pt FT 3-of-3` — actual shooter is #2, fouled on the 3pt attempt. Documented in the scratchpad notes.

### 10d — Contradictions resolved (and how)

- **#3 Davis as PG vs. seeded position.** Seeded as PG (G), confirmed as PG by film. No contradiction — first time the seed and film agree.
- **#2 Gibson as PG (seeded) vs. SG (real).** Seeded as PG, but film clearly shows him as the scoring guard / off-ball receiver, with #3 handling primary PG duties. Resolution: **#2 is the SG / scoring guard; #3 is the primary PG.** Update roster position post-watch.
- **Spire's offense: "no set" (per Films 01 / 02 prior expectation) vs. "structured motion" (per film).** Resolution: **Spire DOES run structured motion offense.** Real finding, materially different from Films 01 / 02. Don't force the "no set" conclusion just because Films 01 / 02 ended up there.
- **#11 great defense (multiple) vs. #11 over-played (Q3 6:24).** Resolution: **#11 is high-quality defender who occasionally over-commits in pressure situations.** Both true. `[CONFIRMED]` strong overall, `[SINGLE GAME SIGNAL]` over-aggression.
- **Spire press: positive (steals) vs. negative (coast-to-coast scores).** Resolution: **Press is high-variance — produces steals AND breakdowns.** Both true. Net judgment: the press is a real weapon but not a settled base.
- **Possession 8 chunk 2 — `Q3 3:12 FT 1-of-2`** initiator listed as `#3` but motion screener as `#4`. Same screen-down-DHO action. No real contradiction; the trio of #3/#2/#4 plus #11 runs the action. Resolved as: #3 initiated (brought ball up), #4 set the down-screen, #11 did the DHO, #2 was the receiver who drove and was fouled. Standard base motion; the FT shooter (and per outcome, presumably the player who got fouled) is `#3` per the scratchpad — but the action description matches #2's typical role. **Possible attribution error in the scratchpad** but not material to ground-truth tendencies.

### 10e — Situations that may not be representative

- **Catch-up loose play in late Q4 (after `Q4 4:00`).** Once Spire was down 11+, possessions devolved into quick-shot 3s, full-court press, steal-and-go transition. These are NOT base half-court possessions. Tag chunk 3 possessions 7–13 as "trailing-game catch-up" rather than base offense. Any TEX output that treats Q4 quick-3 frequency as the base rate will over-count quick shots — the real base rate is closer to chunks 0–2.
- **Q4 elevator screens (poss 16 + poss 7).** Two elevator screens in late-game (down 10+) could be either (a) a real designed action Spire saves for catch-up moments, or (b) a single-game variation. Sample is too small to determine. `[SINGLE GAME SIGNAL]` until film 04 / 05 confirms.
- **LL pulling away in Q3.** The 2-pt → 10-pt LL run between Q3 6:21 and Q3 3:17 is the inflection of the game. Multiple Spire defensive breakdowns in this window (Q3 3:28 drive-and-kick 3, Q3 2:22 coast-to-coast dunk) — these are real but cluster in a single 3-minute window rather than spreading across the game. Pattern is `[CONFIRMED]` (drive-and-kick is the team's weakness across all chunks), but the magnitude of the Q3 run is partly LL execution, not just Spire collapse.
- **#14 vs #11 minute split.** #11 played most minutes; #14 subbed in 3+ times. The base motion / PnR action runs through whichever big is on the floor. When grading, don't penalize TEX for attributing actions to either #11 or #14 as long as the player on the floor is correctly identified.

### 10f — Things you want TEX to get right (watch-items for grading)

1. **Spire DOES have a structured base motion offense.** Weave-top → down-screen for guard from baseline → DHO with big at top → drive. Repeats 25+ times. Any TEX output that says "no real set offense" or "default to iso" is hallucinating from Films 01 / 02 priors. **The structure is real.**
2. **#3 Davis is the PG, NOT a "secondary handler."** Smart, patient, slows the ball deliberately. Initiator of the base motion. TEX must attribute primary-handler / pace-setting / clutch-handling duties to #3.
3. **#2 Gibson drives RIGHT — almost exclusively.** Multiple explicit observations. Scratchpad even flagged "curious to see if he goes left at all." Primary scouting tip for opposing coaches: **force him left.** TEX must catch this hand / direction tendency.
4. **#11 Pur is the offensive hub AND the defensive anchor.** DHO partner in motion, primary screener in PnR, OREB chaser in post, primary PnR screen defender, top of full-court press, hedger / blitzer. Cannot be a generic "rim-runner big." His connector role on offense is the key insight.
5. **Spire is a hedge / blitz / switch team on PnR — NOT a drop team.** Aggressive ball-screen coverage. Opposing teams that are good at attacking blitzes (slip-screens, kick-out shooters) will exploit this.
6. **Drive-and-kick is Spire's primary defensive weakness.** Multiple instances + explicit whole-game wrap-up note. TEX must flag this as the actionable opposing scout tip.
7. **Spire's transition defense is bimodal — works when press succeeds, collapses when press fails.** 3+ coast-to-coast scores allowed. TEX must call out the press as high-variance, not a settled scheme.
8. **Spire ran the SAME motion-DHO-drive sequence 25+ times.** When it works (poss C2-18), they immediately re-run it (poss C2-19). TEX should identify base motion as the team's #1 action with high frequency, not as one of many equally-weighted half-court options.
9. **No Horns, no Spain PnR, no Flex (named), no Iverson cut, no traditional named set.** The motion is screen-the-screener + DHO, not a named set. TEX outputs that label this as "Horns" or "Spain PnR" or "5-out motion" (in the named NBA-set sense) are mis-labeling.
10. **Game shape was a 3rd-quarter blowout — not close late.** Final 2:00 margin was 9–10. Any TEX output that produces confident close-game-late claims from film 03 is hallucinating; §5 must be tagged accordingly.
11. **Cross-film note:** `#32 Jaylan Mitchell` (same name as on Film 01 BBE) DID NOT appear in this Spire game. TEX should NOT cross-reference Film 01 tendencies onto Spire's #32 in this film — there's no observation of him here.

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

