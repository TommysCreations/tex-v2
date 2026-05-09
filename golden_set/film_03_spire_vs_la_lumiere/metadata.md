# Film 03 — Spire Institute Academy vs La Lumiere School

This is the third film in the golden set. Same structural conventions as Films 01 and 02.
Treat this document as static reference data — update it only if the facts themselves
are wrong.

**Important context shift vs Films 01 / 02:** Films 01 and 02 were Nike EYBL **Peach Jam**
games (17U club / AAU summer circuit). Film 03 is from the Nike **EYBL Scholastic**
League — high school **prep program** play during the 2025-26 academic season. Different
roster (school, not club), different game format possibly, different season. Same
methodology, but expect roster overlap with summer-circuit films (e.g. `#32 Jaylan
Mitchell` appears on both Brad Beal Elite (film 01, 17U EYBL summer) and Spire Institute
Academy (film 03, EYBL Scholastic winter) — same player, two programs).

---

## Film in Neon (dev)

| Field | Value |
|---|---|
| film_id (UUID) | `TBD — fill after upload` |
| file_name | `spire_vs_la_lumiere.mp4` (planned) |
| team_id (scouted) | `TBD — fill after creating Spire Institute team row in /admin` |
| user_id | `933c00c7-df54-43a4-ae2d-f36502347cce` (Tommy / admin) |
| duration_seconds | `TBD — from ffprobe after download` |
| chunk_count | `TBD — likely 4 if film is ~75-90 min, 3 if shorter` |
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
| Scouted team | **Spire Institute Academy** (V. Basketball, 2025-26) |
| Opponent | **La Lumiere School** (V. Basketball, 2025-26) |
| Level | High-school prep — Nike EYBL Scholastic (winter season counterpart to summer EYBL) |
| Video source | YouTube (`https://www.youtube.com/watch?v=406zMmbgC0I`) |
| Video title | `TBD — fetch on download` |
| Game clock format | **Four 8-min quarters (32 min regulation).** Confirmed by Tommy as standard EYBL Scholastic / HS prep format. If overtime occurs, confirm OT length on tape. |

**Who is being scouted:** Spire Institute Academy. TEX is learning to scout Spire *as if
Spire were an opponent*. The roster (once seeded) becomes the subject of ground truth —
every action, every player profile, every tendency in `ground_truth.md` refers to a
Spire Institute player. La Lumiere players are opponents and are only referenced
indirectly ("#X drove past La Lumiere's #Y to the rim"). La Lumiere's own roster is
NOT captured in this ground truth (same discipline as Films 01 / 02 with Team Durant
and Arizona Unity).

**EYBL Scholastic note:** This league is the school-season parallel to summer EYBL. Same
brand (Nike), same elite-level talent pool (many EYBL summer-circuit players are at prep
programs like Spire, La Lumiere, Montverde, IMG, Sunrise Christian during the school year),
different schedule and roster. Treat film 03 as a **different scouting context** from films
01–02, even where individual players overlap.

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
clock counts DOWN.

---

## Known players on this roster (as of seed)

Source: Spire Institute Academy V. Basketball public roster page (screenshot, 2025-26
season, captured April 2026). Position mapping: `G → PG`, `W → SF`, `F → PF`, `C → C`
as seeded defaults (same convention as `scripts/seed_bbe_roster.py` and
`seed_rebels_roster.py`). Handedness defaults to `right`; role defaults to
`role_player`. Both are updated as observations emerge from the film.

| # | Name | Pos (seeded) | Ht | Class | Grad | Handedness | Role |
|---|---|---|---|---|---|---|---|
| 0 | Tarris Bouie III | SF (W) | 6'5" | Sr | 2026 | right (default) | role_player (default) |
| 1 | Aiden Dayco-Green | TBD | 6'5" | Jr | 2027 | right (default) | role_player (default) |
| 2 | King Gibson | PG (G) | 6'4" | Jr | 2027 | right (default) | role_player (default) |
| 3 | Darrell Davis | PG (G) | 5'11" | Jr | 2027 | right (default) | role_player (default) |
| 4 | Aiden Derkack | SF (W) | 6'6" | Sr | 2026 | right (default) | role_player (default) |
| 5 | Alex Constanza | SF (W) | 6'9" | Sr | 2026 | right (default) | role_player (default) |
| 11 | Charles Pur | C | 6'9" | Jr | 2027 | right (default) | role_player (default) |
| 12 | Jalen Parker | TBD | 6'4" | So | 2028 | right (default) | role_player (default) |
| 14 | Dorian Rinaldo-Komlan | PF (F) | 6'10" | Sr | 2026 | right (default) | role_player (default) |
| 32 | Jaylan Mitchell | PF (F) | 6'7" | Jr | 2027 | right (default) | role_player (default) |
| 55 | Nolan Nelson | TBD | 6'8" | Jr | 2027 | right (default) | role_player (default) |
| 93 | Collin Ross | C | 6'10" | Sr | 2026 | right (default) | role_player (default) |

**Roster scope (confirmed jerseys, 12):** Jersey range `#0` through `#93`. The current
public roster sheet ends at `#93 Collin Ross` and is NOT scroll-cropped. These 12 are the
only players seeded into Neon (`scripts/seed_spire_roster.py`).

**Carryover / unconfirmed (not seeded):** An older public roster page listed three
additional names that don't appear on the current sheet:

| Name | Source | Status |
|---|---|---|
| Anthony Goring | Older Spire roster page (no jersey, no position, no height) | Unconfirmed — may be cut / transferred / still on team |
| Yair Olano | Older Spire roster page (no jersey, no position, no height) | Unconfirmed — same as above |
| Jeffrey Reynolds | Older Spire roster page (no jersey, no position, no height) | Unconfirmed — same as above |

We are **not certain** which of the two roster sources is the most up-to-date, so these
three names are deliberately retained here as a watch-list. They are **not** seeded into
the DB because we don't have jersey numbers for them, and a fabricated jersey would
pollute TEX's evaluation. Handling on tape:

- If a Spire player appears on the floor with one of the 12 confirmed jerseys → match
  to the seeded roster.
- If a Spire player appears with a jersey NOT in the 12 confirmed list → log in
  `film_watch_notes.md` as `Flagged — uncertain` with the jersey number visible. After
  the watch, check whether the body / face / role matches Goring, Olano, or Reynolds
  and update the seeder + Neon post-watch with the real jersey number.
- If none of the three appear on tape → confirm they were cut / transferred and
  remove this carryover note in a follow-up commit.

**Position notes to validate during first watch:**
- `#1 Aiden Dayco-Green` (6'5" Jr) — listed without a position. At 6'5" likely a wing/SF; confirm.
- `#12 Jalen Parker` (6'4" So) — listed without a position. Likely a guard or wing; confirm.
- `#55 Nolan Nelson` (6'8" Jr) — listed without a position. At 6'8" likely a forward; confirm.
- **Frontcourt-heavy roster:** five players are 6'8" or taller (`#5`, `#11`, `#14`, `#55`, `#93`).
  Two true centers (`#11 Pur`, `#93 Ross`) suggests a possible twin-tower lineup option, or
  one of them mostly DNPs. Watch for which big plays starter minutes vs. which is in rotation.
- **Class breakdown:** 5 seniors (2026), 6 juniors (2027), 1 sophomore (2028). Heavy upperclass roster.

**Cross-film roster note:** `#32 Jaylan Mitchell` (6'7" Jr, 2027) on Spire is almost
certainly the same player as `#32 Jaylan Mitchell` (6'8" 2027 PF) on Brad Beal Elite in
film 01. EYBL summer circuit and EYBL Scholastic winter both pull from the same elite
talent pool — overlap is expected. Treat their film-01 and film-03 profiles as **separate
contexts** (different teammates, different scheme, different tendencies) until proven
identical, but flag the cross-reference for sanity-checking handedness / role claims
across films.

---

## Opponent reference roster (La Lumiere School — NOT captured in ground truth)

*La Lumiere is the opponent in Film 03, not the scouted team. Listed here ONLY for
jersey disambiguation while watching ("La Lumiere's #11 = Gabe Weis," etc.). Do NOT
add La Lumiere players to `roster_players` for Spire. Source: La Lumiere Boys'
National V. Basketball public roster page (screenshot, April 2026 — 13 players,
full pos / ht / class). Same roster is used as the scouted team in Film 05.*

| # | Name | Pos | Ht | Class | Hometown |
|---|---|---|---|---|---|
| 1 | Peyton Kemp | G | 6'2" | Jr (2027) | Clinton Township, MI |
| 2 | Devin Cleveland | G | 6'3" | Jr (2027) | Chicago, IL |
| 3 | Jacob Webber | G | 6'6" | Sr (2026) | Kearney, NE |
| 5 | Ben Levy | G | 6'3" | Jr (2027) | Melbourne, Australia |
| 10 | Jonathan Sanderson | G | 6'3" | Sr (2026) | Ann Arbor, MI |
| 11 | Gabe Weis | F | 6'7" | Sr (2026) | Springfield, KY |
| 15 | Cruz Mactavish | G | 6'5" | Jr (2027) | Sydney, Australia |
| 20 | Ferlandes Wright | F | 6'8" | Jr (2027) | Louisville, KY |
| 21 | Rivers Knight | F | 6'9" | Sr (2026) | Durham, NC |
| 22 | Will Chang | G | 6'2" | Sr (2026) | Taipei, Taiwan |
| 24 | Cuba Smith | G | 6'3" | Sr (2026) | Merrillville, IN |
| 33 | Charlie Yalden | C | 6'8" | Fr (2029) | Wiesbaden, Germany |
| 44 | Gan Solongo | C | 7'0" | Sr (2026) | Zuumod, Mongolia |

*Updated April 2026 from a fresh capture of the official La Lumiere page. The earlier
capture for Film 03 listed only 12 players (no `#15 Cruz Mactavish`) and had no
position / height / class data. The 13-player table above replaces it; both Film 03
and Film 05 reference rosters now agree.*

---

## Open questions to answer during the first watch

*Same questions as Films 01 / 02's templates — update / add as the roster becomes clearer.*

- Who is the primary ball-handler / PG of Spire? Likely `#2 Gibson` or `#3 Davis` (both seeded G), but confirm.
- Which players are left-handed? (Priors: ~10–15% of roster — none confirmed yet.)
- Who is the primary initiator / secondary handler / spacer / screener / finisher?
- Of the two true centers (`#11 Pur`, `#93 Ross`), who is the starter? Do they play together (twin-tower) or alternate?
- Are any players on this film not on the 12-player seeded roster (call-ups, late additions)? Specifically watch for Anthony Goring, Yair Olano, Jeffrey Reynolds — they were on an older roster page (no jerseys listed there) and we're unsure which roster is the most current. If any of them appear on tape, log the jersey + a body description and we'll add them to the seeder post-watch.
- What's Spire's base defense, and does it change during the game?
- Are there any structural half-court sets (Horns, Spain PnR, Flex, etc.), or does the team default to no-set iso like BBE / Rebels did? (Real comparison point — do not assume one way. Prep-program teams often run more structured offenses than club AAU teams because they get year-round practice time.)

---

## What to do when you have corrections to this metadata

The DB columns are the source of truth for `film_id`, `team_id`, and `user_id`
once populated. If this document falls out of sync with Neon, the DB wins. Update
this file and commit the diff.

The seeded roster is editable post-hoc through the `/admin` UI or by modifying
`scripts/seed_spire_roster.py` and re-running. Either is fine for dev; neither
is allowed in production without a migration.

---

*Last updated: Golden set initialization — film_03 scaffold (pre-upload, pre-watch).*
