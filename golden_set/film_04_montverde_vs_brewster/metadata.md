# Film 04 — Montverde Academy vs Brewster Academy

This is the fourth film in the golden set. Same structural conventions as Films 01 / 02 / 03.
Treat this document as static reference data — update it only if the facts themselves
are wrong.

**Important context (same league as Film 03):** Film 04 is from the Nike **EYBL Scholastic**
League — high school **prep program** play during the 2025-26 academic season. Format
confirmed as **four 8-min quarters (32 min regulation)**. Two of the most well-known prep
programs in the country face off here: Montverde Academy (Florida) vs Brewster Academy
(New Hampshire). Same brand (Nike), same elite-level talent pool, same scholastic schedule
as Film 03.

---

## Film in Neon (dev)

| Field | Value |
|---|---|
| film_id (UUID) | `TBD — fill after upload` |
| file_name | `montverde_vs_brewster.mp4` (planned) |
| team_id (scouted) | `TBD — fill after creating Montverde Academy team row in /admin` |
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
| Scouted team | **Montverde Academy** (V. Basketball, 2025-26) |
| Opponent | **Brewster Academy** — Boys' National team (V. Basketball, 2025-26) |
| Level | High-school prep — Nike EYBL Scholastic |
| Video source | YouTube (`https://www.youtube.com/watch?v=tBnjFA64RSc`) |
| Video title | `TBD — fetch on download` |
| Game clock format | **Four 8-min quarters (32 min regulation).** Confirmed by Tommy as standard EYBL Scholastic / HS prep format. If overtime occurs, confirm OT length on tape. |

**Who is being scouted:** Montverde Academy. TEX is learning to scout Montverde *as if
Montverde were an opponent*. The roster (once seeded) becomes the subject of ground truth —
every action, every player profile, every tendency in `ground_truth.md` refers to a
Montverde player. Brewster players are opponents and are only referenced indirectly
("#X drove past Brewster's #Y to the rim"). Brewster's own roster is NOT captured in this
ground truth (same discipline as Films 01–03).

**EYBL Scholastic note:** This is the school-season parallel to summer EYBL. Same brand
(Nike), same elite-level talent pool. Many EYBL summer-circuit players play at prep
programs like Montverde, Brewster, Spire, La Lumiere, IMG, and Sunrise Christian during
the school year. Montverde in particular has been the dominant prep-school program of
the past decade — expect a structured, well-coached team.

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
film is shorter than expected (e.g. 60 min), TEX may split into 3 chunks instead of 4.*

Record **in-game clock time** in `film_watch_notes.md`, not tape time. Each quarter's
clock counts DOWN from 8:00.

---

## Known players on this roster (as of seed)

Source: Montverde Academy V. Basketball public roster page (screenshot, 2025-26 season,
captured April 2026). Position mapping convention (same as Films 01–03):
`G → PG`, `F → PF`, `F/C → C`, `C → C` as seeded defaults. Handedness defaults to
`right`; role defaults to `role_player`. Both are updated as observations emerge from the
film.

| # | Name | Pos (seeded) | Ht | Class | Hometown | Notes |
|---|---|---|---|---|---|---|
| 1 | Joe Philon III | PF (F) | 6'8" | Sr | Tampa, FL | Likely a primary scorer / featured player at 6'8" Sr — confirm tendencies on tape |
| 2 | Dhani Miller | PG (G) | 6'3" | Sr | Roselle, NJ |   |
| 3 | Javion Tyndale | PG (G) | 5'9" | Jr | Mississauga, ON, Canada | True point guard size — almost certainly the lead handler |
| 5 | Lincoln Cosby | PF (F) | 6'10" | Jr | Cincinnati, OH | 6'10" listed as F — may be the true 5; confirm |
| 10 | Nikos Koulisianis | PF (F) | 6'9" | Sr | Brno, Czech Republic | International big — confirm role (stretch-4 vs interior) |
| 11 | Oneal Delancy | PG (G) | 6'3" | Jr | St Petersburg, FL |   |
| 12 | Sebastien Ndour | PG (G) | 6'7" | Jr | Mbour, Senegal | 6'7" listed as G is unusual — confirm whether he plays as a wing or oversized handler |
| 25 | Trace Lopez | C (F/C) | 6'9" | So | Phoenix, AZ | F/C designation + 6'9" + So = developmental big; confirm minutes |
| 32 | Malachi Booker | PF (F) | 6'7" | Jr | Houston, TX |   |
| 33 | Jayden Hodge | PG (G) | 6'6" | Sr | Limburg, Belgium | 6'6" G could be combo guard or wing |
| 42 | Derek Daniels | C (F/C) | 6'8" | Jr | Washington, DC |   |

**Roster scope:** 11 players total, jerseys `#1, #2, #3, #5, #10, #11, #12, #25, #32, #33, #42`.
The published roster page ends at #42 Daniels. Listed players span 5'9" to 6'10" — well-balanced
size. International recruiting is heavy (Canada, Czech Republic, Senegal, Belgium) — typical
for Montverde.

**Position notes to validate during first watch:**
- `#1 Joe Philon III` (6'8" Sr) — most likely primary scorer based on size + class. Confirm role_tag.
- `#3 Javion Tyndale` (5'9" Jr) — only sub-6'0" player on the roster. Almost certainly the lead PG.
- `#12 Sebastien Ndour` (6'7" Jr) — listed as G but at 6'7" likely a wing / point-forward. Confirm.
- `#33 Jayden Hodge` (6'6" Sr) — listed as G but tall for a guard. Confirm whether he plays SG vs SF.
- **Frontcourt depth:** Five players are 6'8" or taller (`#1`, `#5`, `#10`, `#25`, `#42`). Possible
  twin-tower lineup if two of `#5 Cosby` / `#10 Koulisianis` / `#25 Lopez` / `#42 Daniels` share
  the floor. Watch rotations.
- **Class breakdown:** 4 seniors (2026), 5 juniors (2027), 1 sophomore (2028), 1 unconfirmed
  (#3 Tyndale class year reads "Jr" → 2027). Heavy junior/senior roster — typical of a
  championship-caliber prep program.

**Cross-film roster notes:** Compare to Spire (Film 03) and BBE / Rebels (Films 01-02) for
any players who may have appeared on multiple programs in the same talent pool. None of
these 11 names overlap with Films 01-03 to my knowledge — flag if a name pops up that you
recognize from earlier films.

---

## Opponent reference roster (Brewster Academy — NOT captured in ground truth)

*Brewster is the opponent, not the scouted team. Listed here ONLY for jersey
disambiguation while watching ("Brewster's #1 = Darien Moore," etc.). Do NOT add
Brewster players to `roster_players` in Neon. Source: Brewster Academy "Boys' National"
V. Basketball public roster, 2025-26.*

| # | Name | Pos | Ht | Class | Hometown / Commit |
|---|---|---|---|---|---|
| 0 | Antonio Pemberton | PG | 6'1" | Jr | Methuen, MA |
| 1 | Darien Moore | G | 6'2" | Sr | Hudson, NY / Seton Hall (committed) |
| 2 | Michai White | PG | 6'1" | So | Hackensack, NJ |
| 3 | Reece Ayala | PG | 6'4" | Jr | Lawrence, MA |
| 5 | Markus Kerr | G | 6'6" | Jr | Charlotte, NC |
| 10 | Kevin Wheatley | G | 6'6" | So | Rahway, NJ |
| 13 | Kaiden Francis | F | 6'7" | Sr | Brooklyn, NY |
| 21 | Tayden Langdon | G | 6'2" | Jr | Birmingham, MI |
| 25 | Brayden Jones | F | 6'8" | Sr | Wethersfield, CT |
| 30 | Mark Burns | F | 6'9" | Jr | Belfast, Ireland |
| 32 | Eric Jacobsen | F | 6'11" | Sr | Colorado Springs, CO |

*Position / height / class fields were populated on the published Brewster sheet — captured
here verbatim. The "Boys' National" team is Brewster's elite varsity squad (separate from
their Postgrad team). 11 players total.*

---

## Open questions to answer during the first watch

*Same shape as Films 01-03. Update / refine as the roster becomes clearer on tape.*

- Who is Montverde's primary ball-handler / PG? Strong prior on `#3 Javion Tyndale` (only sub-6'0" player), but confirm.
- Which players are left-handed? (Priors: ~10–15% of any roster — none confirmed yet.)
- Who is the primary scorer? Strong prior on `#1 Joe Philon III` (6'8" Sr), but confirm volume + zones.
- Who is the primary screener / roller / popper? Watch the bigs (`#5 Cosby`, `#10 Koulisianis`, `#25 Lopez`, `#42 Daniels`).
- Of the four 6'8"+ bigs, who starts? Who DNPs? Who plays together (twin-tower)?
- What's Montverde's base defense, and does it change during the game?
- **Important for prep programs:** Are there any structural half-court sets (Horns, Spain PnR, Flex, motion continuities, Princeton, etc.)? Montverde is famously well-coached — this is a real likelihood, unlike Films 01/02 where AAU teams ran no-set iso. **Don't assume zero structure — let the film tell you.**
- Is there a transition / press identity? Montverde historically pushes pace.

---

## What to do when you have corrections to this metadata

The DB columns are the source of truth for `film_id`, `team_id`, and `user_id`
once populated. If this document falls out of sync with Neon, the DB wins. Update
this file and commit the diff.

The seeded roster is editable post-hoc through the `/admin` UI or by modifying
`scripts/seed_montverde_roster.py` and re-running. Either is fine for dev; neither
is allowed in production without a migration.

---

*Last updated: Golden set initialization — film_04 scaffold (pre-upload, pre-watch).*
