# Film 05 — La Lumiere School vs Oak Hill Academy

This is the fifth (final) film in the golden set. Same structural conventions as Films 01–04.
Treat this document as static reference data — update it only if the facts themselves
are wrong.

**Important context (same league as Films 03–04):** Film 05 is from the Nike **EYBL Scholastic**
League — high school **prep program** play during the 2025-26 academic season. Format
confirmed as **four 8-min quarters (32 min regulation)**.

**Cross-film note vs Film 03:** La Lumiere is the **scouted team** in Film 05, but was the
**opponent** in Film 03 (Spire Institute Academy vs La Lumiere). Same La Lumiere roster
applies, sourced from the official Boys' National team page (April 2026 snapshot, 13 players).
Film 03's metadata.md / film_watch_notes.md La Lumiere reference roster has been updated
to match this most-current snapshot for consistency.

---

## Film in Neon (dev)

| Field | Value |
|---|---|
| film_id (UUID) | `TBD — fill after upload` |
| file_name | `la_lumiere_vs_oak_hill.mp4` (planned) |
| team_id (scouted) | `TBD — fill after creating La Lumiere School team row in /admin` |
| user_id | `933c00c7-df54-43a4-ae2d-f36502347cce` (Tommy / admin) |
| duration_seconds | `TBD — from ffprobe after download` |
| chunk_count | `TBD — likely 3-4 depending on broadcast length` |
| status | `TBD — will be 'processed' once all extract_chunk tasks finish` |
| source codecs | `TBD — confirm via ffprobe; expected H.264 + AAC after yt-dlp merge` |
| raw file size | `TBD` |
| compressed size | `TBD — worker re-encodes to 720p H.264 CRF 28 if raw > 1.8 GB` |

---

## Game context

| Field | Value |
|---|---|
| Event | **Nike EYBL Scholastic League** (2025-26 season) |
| Year | 2025-26 academic year (likely game date in late 2025 / early 2026) |
| Scouted team | **La Lumiere School** — Boys' National team (V. Basketball, 2025-26) |
| Opponent | **Oak Hill Academy** (V. Basketball, 2025-26) |
| Level | High-school prep — Nike EYBL Scholastic |
| Video source | YouTube (`https://www.youtube.com/watch?v=1R3fHSYVcXU`) |
| Video title | `TBD — fetch on download` |
| Game clock format | **Four 8-min quarters (32 min regulation).** Confirmed by Tommy as standard EYBL Scholastic / HS prep format. If overtime occurs, confirm OT length on tape. |

**Who is being scouted:** La Lumiere School. TEX is learning to scout La Lumiere *as if
they were an opponent*. The roster (once seeded) becomes the subject of ground truth —
every action, every player profile, every tendency in `ground_truth.md` refers to a
La Lumiere player. Oak Hill players are opponents and are only referenced indirectly
("#X drove past Oak Hill's #Y to the rim"). Oak Hill's own roster is NOT captured in
this ground truth.

**Important EYBL Scholastic note:** Both La Lumiere and Oak Hill Academy are top-tier
prep programs with a long history of producing high-major and NBA talent. Both teams
practice year-round and likely run more structured offense than club AAU teams (Films
01–02). Watch carefully for **named sets** — same discipline as Films 03–04.

---

## Chunk boundaries

Each chunk is analyzed independently by Prompt 0A (extraction). TEX splits on
25-minute wall-clock boundaries (`-segment_time 1500`). Game state column is a
first-pass estimate — fill in `Actual game clock window` at the top of each chunk
section in `film_watch_notes.md` during the watch.

| Chunk | Tape start | Tape end | Duration | Approximate game state (estimate) |
|---|---|---|---|---|
| C0 | 00:00 | 25:00 | 25:00 | `TBD — fill after duration is known` |
| C1 | 25:00 | 50:00 | 25:00 | `TBD` |
| C2 | 50:00 | 1:15:00 | 25:00 | `TBD` |
| C3 | 1:15:00 | end | varies | `TBD — depends on total duration` |

*Total film = TBD seconds. Update this table once `ffprobe` confirms duration. If the
film is shorter than expected, TEX may split into 3 chunks instead of 4.*

Record **in-game clock time** in `film_watch_notes.md`, not tape time. Each quarter's
clock counts DOWN from 8:00.

---

## Known players on this roster (as of seed)

Source: La Lumiere School Boys' National V. Basketball public roster page (screenshot,
April 2026, 2025-26 season — 13 players, full position / height / class data). Position
mapping convention (same as Films 01–04): `G → PG`, `F → PF`, `C → C` as seeded defaults
(flag tall guards for review). Handedness defaults to `right`; role defaults to
`role_player`. Both updated as observations emerge from the film.

| # | Name | Pos (seeded) | Ht | Class | Hometown | Notes |
|---|---|---|---|---|---|---|
| 1 | Peyton Kemp | PG (G) | 6'2" | Jr (2027) | Clinton Township, MI |   |
| 2 | Devin Cleveland | PG (G) | 6'3" | Jr (2027) | Chicago, IL |   |
| 3 | Jacob Webber | PG (G) | 6'6" | Sr (2026) | Kearney, NE | 6'6" listed as G — confirm wing vs oversized handler |
| 5 | Ben Levy | PG (G) | 6'3" | Jr (2027) | Melbourne, Australia |   |
| 10 | Jonathan Sanderson | PG (G) | 6'3" | Sr (2026) | Ann Arbor, MI |   |
| 11 | Gabe Weis | PF (F) | 6'7" | Sr (2026) | Springfield, KY |   |
| 15 | Cruz Mactavish | PG (G) | 6'5" | Jr (2027) | Sydney, Australia | 6'5" G — confirm wing vs combo guard |
| 20 | Ferlandes Wright | PF (F) | 6'8" | Jr (2027) | Louisville, KY |   |
| 21 | Rivers Knight | PF (F) | 6'9" | Sr (2026) | Durham, NC | 6'9" listed as F — could be true 5; confirm |
| 22 | Will Chang | PG (G) | 6'2" | Sr (2026) | Taipei, Taiwan |   |
| 24 | Cuba Smith | PG (G) | 6'3" | Sr (2026) | Merrillville, IN |   |
| 33 | Charlie Yalden | C | 6'8" | Fr (2029) | Wiesbaden, Germany | **Freshman 6'8" C** — likely developmental minutes; confirm role |
| 44 | Gan Solongo | C | 7'0" | Sr (2026) | Zuumod, Mongolia | True 7-footer — confirm starter vs rotation; rim-protector role |

**Roster scope:** 13 players total, jerseys range `#1` through `#44`. The published page
shows La Lumiere as "Boys' National" team (their elite varsity squad). Heavy international
recruiting (Australia ×2, Taiwan, Germany, Mongolia). Three legitimate frontcourt bodies
(`#11 Weis`, `#20 Wright`, `#21 Knight`, `#33 Yalden`, `#44 Solongo` — five if you count
both centers).

**Position notes to validate during first watch:**
- `#3 Jacob Webber` (6'6" Sr G) — listed as guard but tall; confirm wing vs handler.
- `#15 Cruz Mactavish` (6'5" Jr G) — same situation; confirm role.
- `#21 Rivers Knight` (6'9" Sr F) — likely a true 4 or potential small-ball 5.
- `#33 Charlie Yalden` (6'8" Fr C) — freshman big; confirm minutes vs garbage time.
- `#44 Gan Solongo` (7'0" Sr C) — true 7-footer is rare; confirm whether he's the starter
  or platoons with Yalden.
- **Backcourt depth:** Eight guards on the roster (`#1, #2, #3, #5, #10, #15, #22, #24`).
  Heavy guard rotation likely. Watch for which 2-3 actually play meaningful minutes.
- **Class breakdown:** 6 seniors (2026), 6 juniors (2027), 1 freshman (2029). Heavy
  upperclass roster typical of a championship-caliber prep program.

**Cross-film roster sanity check:**
- Same 12 players as Film 03's La Lumiere reference roster, **plus** `#15 Cruz Mactavish`
  (newly added or previously missed). Film 03's reference roster has been updated
  retroactively to match.
- No player overlap with Spire (Film 03), Brad Beal Elite (Film 01), Florida Rebels (Film 02),
  or Montverde (Film 04) to my knowledge — flag if a name pops up that you recognize from
  earlier films.

---

## Opponent reference roster (Oak Hill Academy — NOT captured in ground truth)

*Oak Hill is the opponent, not the scouted team. Listed here ONLY for jersey
disambiguation while watching ("Oak Hill's #21 = Kuol Kuol," etc.). Do NOT add
Oak Hill players to `roster_players` in Neon.*

**Sources:**
- **Primary**: RealGM HS roster page (`basketball.realgm.com/highschool/rosters/2/Oak-Hill-Academy`) — full Pos / Ht / Class for all 12 players.
- **Cross-check**: 247Sports / On3 / ESPN individual recruit profiles, plus Oak Hill's own athletics site (`ohaathletics.com/pages/roster`) for handful of players.
- **Hometowns**: Nike EYBL Scholastic published roster page (matches Tommy's screenshot).

| # | Name (Oak Hill page / recruiting alias) | Pos | Ht | Class | Hometown | Notes |
|---|---|---|---|---|---|---|
| 0 | Kamari Lawson *(Kamauri Lawson on recruiting sites)* | G (PG) | 6'0" | Sr (2026) | Baltimore, MD | Transferred from St. Frances Academy. Listed 5'9"–6'0" depending on source; RealGM has 6'0". |
| 1 | Janon Singh | F (SF) | 6'6"–6'7" | Jr (2027) | Rex, GA | RealGM 6'7" / 247 6'6". 247 lists hometown as Loganville, GA — Tommy's screenshot has Rex, GA. |
| 2 | Korie Corbett | G (SG/SF) | 6'4" | Sr (2026) | Columbia, SC | Former Ridge View HS. **UAB commit.** 6'4" combo wing. |
| 3 | Ethan Mgbako | F (SF) | 6'6" | Sr (2026) | Somerset, NJ | **Vanderbilt commit (4-star, #65 nationally, 2026 class).** 215 lbs. |
| 4 | LJ Smith *(L.J. Smith IV)* | G (combo / SG) | 6'4" | Jr (2027) | Lincolnton, NC | Combo guard. |
| 5 | Jayden Newll *(Jayden Newell — published-page typo)* | G (PG) | 6'1" | Jr (2027) | Chicago, IL | Transferred from Simeon Career Academy. Confirmed name spelling: "Newell". |
| 11 | Zyon McGlone | PG | 5'11" | Jr (2027) — **see flag** | (unlisted on Oak Hill page) | **Class conflict:** Tommy's screenshot of the Oak Hill page shows `Fr.`; RealGM + Times News (Feb 2026 game report) both have him as `Jr` 5'11". Flagging — likely the published page is wrong. |
| 12 | Tyler Hallier | GF (SG/SF) | 6'4" | Sr (2026) | Las Vegas, NV | Background: tennis-to-basketball convert (Spain → Oak Hill). |
| 20 | Julius Kimani | C | 7'2" | Jr (2027) | Exton, PA | True 7-footer. |
| 21 | Kuol Kuol *(Kuol Deng on recruiting sites)* | C | 6'10" | Sr (2026) | Savannah, GA (via South Sudan) | Transferred from Calvary Day for senior year. 210 lbs. |
| 24 | Mark Leung | G | 5'10"–5'11" | Sr (2026) — **see flag** | Hong Kong, China | **Class conflict:** RealGM has Sr 5'11", oha athletics page has 2027 / 5'10". Flagging — using RealGM as primary. |
| 33 | Kimario Sherman, Jr. | C | 7'0" | Jr (2027) | Atlanta, GA | Second 7-footer. |

**Position-mapping note (TEX convention applied):**
- RealGM uses `G / GF / F / PG / C`. Mapped above to TEX-style `(role)` — confirm on tape.
- Heavy frontcourt: **three 6'10"+ bigs** (`#20 Kimani 7'2"`, `#21 Kuol 6'10"`, `#33 Sherman 7'0"`). Likely platoon, not all on the floor at once. Watch for which one is the starter.
- Two senior wings + commits: `#3 Mgbako` (Vanderbilt, 6'6" SF) and `#2 Corbett` (UAB, 6'4" SG/SF) — likely Oak Hill's primary scorers.
- PG group: `#0 Lawson 6'0" Sr`, `#5 Newell 6'1" Jr`, `#11 McGlone 5'11" Jr` — three legitimate point guards. Watch which one initiates most.

**Validation flags noted (handle on tape):**
- `#11 McGlone` class year (Fr per published page vs Jr per other sources).
- `#24 Leung` class year (Sr per RealGM vs Jr per Oak Hill's own page).
- `#5 Newell` published-page name typo ("Newll" → "Newell").
- `#1 Singh` hometown (Rex vs Loganville GA — same metro Atlanta region).

These are all opponent-side notes — they don't affect ground truth. Logged here so we
don't get confused mid-watch when the scoreboard / ESPN ticker shows a different name.

---

## Open questions to answer during the first watch

*Same shape as Films 01–04. Update / refine as the roster becomes clearer on tape.*

- Who is La Lumiere's primary ball-handler / PG? Eight guards on the roster — which 2-3 actually play primary handler minutes?
- Which players are left-handed? (Priors: ~10–15% of any roster — none confirmed yet.)
- Who is the primary scorer? Strong roster of seniors (`#3 Webber`, `#10 Sanderson`, `#11 Weis`, `#21 Knight`, `#22 Chang`, `#24 Smith`, `#44 Solongo`) — confirm volume + zones.
- Of the two true centers (`#33 Yalden Fr`, `#44 Solongo Sr`), who starts? Do they play together (twin-tower with Solongo at 5 + Yalden as 4)?
- What's La Lumiere's base defense, and does it change during the game?
- **Important for prep programs:** Are there structural half-court sets (Horns, Spain PnR, Flex, motion continuities, Princeton, etc.)? La Lumiere is well-coached — this is a real likelihood, unlike Films 01/02 where AAU teams ran no-set iso. **Don't assume zero structure — let the film tell you.**
- Is there a transition / press identity? La Lumiere historically pushes pace.
- **Oak Hill positions / heights:** Resolved via RealGM + 247/On3/ESPN cross-check (April 2026). Two minor class-year conflicts flagged in the Oak Hill reference table above (`#11 McGlone` and `#24 Leung`); resolve on tape if it matters.

---

## What to do when you have corrections to this metadata

The DB columns are the source of truth for `film_id`, `team_id`, and `user_id`
once populated. If this document falls out of sync with Neon, the DB wins. Update
this file and commit the diff.

The seeded roster is editable post-hoc through the `/admin` UI or by modifying
`scripts/seed_la_lumiere_roster.py` and re-running. Either is fine for dev; neither
is allowed in production without a migration.

---

*Last updated: Golden set initialization — film_05 scaffold (pre-upload, pre-watch).*
