# PROMPTS.md — TEX v2

All 6 section prompts. Versioned. With changelog.
These are the exact strings loaded from `backend/prompts/*.txt` at report generation time.
Every prompt has a VERSION header. That version is saved to `report_sections.prompt_version`
and `corrections.prompt_version` on every report. Never edit a prompt without incrementing
the version and adding a changelog entry. Cache entries from prior versions are stale — see SCHEMA.md.

Prompts are the highest-leverage asset in the system. One word change can break output quality for
every report until the next correction cycle surfaces it. Change prompts deliberately, version them
always, and run the eval questions in EVALS.md against any changed prompt before deploying.

---

## HOW PROMPTS ARE LOADED

```python
# services/prompts.py (canonical — copy this to verify edits)
def load_prompt(section_type: str) -> tuple[str, str]:
    """Load a prompt file and return (prompt_text, version)."""
    path = PROMPTS_DIR / f"{section_type}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    raw = path.read_text()
    first_line, _, rest = raw.partition("\n")
    if not first_line.startswith("VERSION:"):
        raise ValueError(f"Prompt file {path} missing VERSION header")
    version = first_line.replace("VERSION:", "").strip()

    # Split on --- delimiter — must be on its own line (with a preceding newline).
    parts = raw.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError(f"Prompt file {path} missing --- delimiter")
    prompt_text = parts[1].strip()

    return prompt_text, version
```

The `---` delimiter must be on its own line **with a preceding newline** — the loader splits on
`"\n---\n"`, not `"---\n"`. Everything below the delimiter is sent to Gemini verbatim. No
pre-processing except roster injection for sections 1-4 and `{chunk_index}` / `{total_chunks}` /
`{start_min}` / `{end_min}` substitution for Prompt 0A.

---

## CONTEXT STRUCTURE — SECTIONS 1-4

Sections 1-4 receive a Gemini context cache containing:
1. All film chunk URIs (video content — the full game film)
2. The roster string (formatted by `format_roster_for_prompt()`)

The prompt text is sent as the user message against this cached context. The roster is in the
cache, not in the prompt. The prompt does not need to re-describe the roster format — Gemini
reads the cache and the prompt together.

**What Gemini sees for sections 1-4:**
```
[Context cache]:
  [video: chunk_000.mp4]
  [video: chunk_001.mp4]
  ...
  ROSTER:
    #3 Marcus Williams, PG, 6'2", primary_initiator, right-handed
    #10 Jordan Hayes, SF, 6'5", spacer
    ...

[User message]:
  {section_prompt_text}
```

---

## CONTEXT STRUCTURE — SECTIONS 5-6

Sections 5-6 receive no video. They receive sections 1-4 text output as a structured context string.

**What Gemini Flash sees for section 5:**
```
[User message]:
  SCOUTING REPORT CONTEXT — [TEAM NAME]
  Generated from game film analysis. Use this as the complete basis for your output.

  === OFFENSIVE SETS ===
  {section_1_content}

  === DEFENSIVE SCHEMES ===
  {section_2_content}

  === PICK AND ROLL COVERAGE ===
  {section_3_content}

  === INDIVIDUAL PLAYER PROFILES ===
  {section_4_content}

  ---
  {section_5_prompt_text}
```

**What Gemini Flash sees for section 6:**
Same as above, plus section 5 output appended before the section 6 prompt.

---

## PROMPT FILE FORMAT

Every `.txt` file in `backend/prompts/` follows this exact format:

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
[prompt text]
```

The `---` line is the delimiter. It must be on its own line with no leading spaces.
The prompt text begins on the line immediately after `---`.

---

## PROMPT 0 — CHUNK SYNTHESIS

**Files:** `backend/prompts/chunk_extraction.txt` + `backend/prompts/chunk_synthesis.txt`
**Models:** Gemini **2.5 Pro** (Stage 1 — extraction, **video**) + Gemini **2.5 Flash** (Stage 2 — synthesis, **text-only** — see `tasks/film_processing.py::run_chunk_synthesis`; AGENTS.md Prompt 0B).
**Input:** Raw video chunks (extraction) → concat of chunk extraction outputs + roster (synthesis)
**Output:** A unified full-game intelligence document stored in **`film_analysis_cache.synthesis_document`** and passed into downstream section generation (see **`services/ai/gemini.py`** — synthesis-only / Option 3: sections **1–4** receive **text** context, not chunk video)

This is the most important prompt engineering problem in the product. Sections 1-4 are only
as accurate as the foundation they build on. If the synthesis is wrong — miscounted sets,
unreconciled vocabulary, lost half-time adjustments — all 6 sections inherit those errors
and every correction Tommy makes traces back to a synthesis failure, not a section failure.

Prompt 0 is not optional. It is not a performance optimization. It is the mechanism that
turns N partial views of a game into one coherent ground truth.

---

### WHY TWO STAGES

A single synthesis call that receives all raw video simultaneously sounds simpler but
creates a harder problem: asking Gemini to simultaneously perceive, count, reconcile,
and structure a 2-hour game in one pass produces lower accuracy than separating perception
from synthesis. The extraction pass asks Gemini to watch and describe. The synthesis pass
asks it to think. These are different cognitive tasks and perform better when separated.

**Stage 1 — Per-Chunk Extraction (run in parallel, one call per chunk):**
Each chunk gets a structured extraction pass. Output is a machine-parseable observation
log — what was seen, how many times, who did it. No interpretation. No strategy. Pure observation.
These run in parallel alongside each other. 5 chunks = 5 simultaneous Gemini calls.

**Stage 2 — Synthesis (one call, receives all extraction outputs):**
Takes all chunk extraction outputs as text input. No video. Reconciles vocabulary,
aggregates counts, identifies timeline changes, flags contradictions, and produces the
unified full-game intelligence document that sections 1-4 consume.

---

### PIPELINE POSITION

```
Film chunks uploaded to Gemini File API
    │
    ├── Chunk extraction pass (parallel — one per chunk, Gemini 2.5 Pro)
    │   ├── chunk_000: extraction output → saved to DB
    │   ├── chunk_001: extraction output → saved to DB
    │   ├── chunk_002: extraction output → saved to DB
    │   └── chunk_003: extraction output → saved to DB
    │
    └── Synthesis pass (one call, text-in text-out, Gemini 2.5 Flash)
            Input: all chunk extraction outputs + roster
            Output: unified game intelligence document
            Saved to: film_analysis_cache.synthesis_document (Phase 2+)
                      passed as text alongside roster when sections 1-4 generate (Option 3)
```

The synthesis document is stored in **`film_analysis_cache`** and keyed by **`file_hash`** + composite **`prompt_version`** from **`services/prompt_versions.py`** (section bundle + preprocess headers).

**Downstream consumption (today — synthesis-only mode / Option 3):** Sections **1–4** do **not** re-read chunk video together with the synthesis document. **`create_context_cache()`** carries **synthesis + roster as text only** (see **`services/ai/gemini.py`**). The **`vertex:no-cache:`** sentinel path routes **`analyze_video_cached()`** to a **Gemini 2.5 Pro** prompt that reads **[text_context, prompt]** — the model's "ground truth window" for the game is the **synthesis document plus section prompt discipline**, not the raw film. *If* Google context caching for multi-chunk video is restored in the future, this document may again be **prepended** alongside video; the spec text below was written for that world—**the repo code path is authoritative.**

---

### STAGE 1 — CHUNK EXTRACTION PROMPT

**File:** `backend/prompts/chunk_extraction.txt`

**Canonical text (2026-05-19):** The live prompt in git is the source of truth — **`VERSION: v1.6`** on disk. The fenced copy below is a verbatim mirror of `backend/prompts/chunk_extraction.txt` as of this update. If the `.txt` file is bumped (e.g. v1.7), the mirror here MUST be updated in the same PR — the cache key derives from the `.txt` headers, not from this doc.

```
VERSION: v1.6
CHANGELOG:
  v1.6 — Canonical geometry for 5-out vs 1-4 flat/high PnR; forbid burying high PnR in generic 5-out; transition vs fast bring-up tempo block; two-layer defended PnR (big + ball defender); score sources + no bogus final; opponent standout trigger; OOB formation sweep; mandatory segment N for defended PnRs.
  v1.5 — Reactive-vs-zone tag on offense (splits zone answers from base half-court sets in synthesis); chunk cue for 2-2-1 / guards-up vs zone shell.
  v1.4 — Roster spelling enforced character-for-character; Horns vs 5-out disambiguation; zone shell cues; opponent never gets invented names; transition count definition tightened; sub reporting tied to roster.
  v1.3 — Named-set discipline (Horns / 1-4 flat vs generic 5-out); opponent zone + standout vs scouted D; scoreboard reconciliation; subs/injury; thin-sample caveats for PnR defense.
  v1.2 — Paired with `chunk_synthesis` for `film_analysis_cache` key (see `services/prompt_versions.py`).
  v1.1 — Roster sent inline ({roster}); chunk index/total and segment minute window injected by worker.
  v1.0 — Initial version.
---
You are analyzing one segment of a complete basketball game film.
This segment is chunk {chunk_index} of {total_chunks}, covering approximately minutes {start_min} to {end_min} of game film runtime (elapsed minutes from the start of the full uploaded video — not necessarily the arena scoreboard clock).

ROSTER for the team being scouted (authoritative):
Copy **every scouted-team player name from the roster block below exactly** — same spelling and punctuation — in every PLAYERS line and every #[JERSEY] [NAME] block. If the announcer uses a different spelling or nickname, keep the **roster** spelling and note the announcer under FLAGGED OBSERVATIONS. Do not "correct" the roster line to match the announcer.

You do NOT have the opponent’s roster. For opponent players:
  • Use the form **opponent #[N]** in all standouts and defensive notes.
  • You may add a **heard-only** tag in parentheses: `opponent #0 (announcer said "Pemberton")` — do **not** invent or guess last names you did not clearly hear tied to that number. Never write opponent names as if they were verified facts.

{roster}

Your job is to produce a structured observation log of everything that happens in this segment.
This is a perception task only. Do not interpret, strategize, or draw conclusions.
Document what you see. Use precise counts. Use jersey numbers and **exact** roster names for the scouted team only.

CANONICAL TEX LABELS (geometry — use these names so synthesis can aggregate; do not collapse different pictures into one bucket):

  **5-out:** All **five** offensive players are clearly **outside / above the three-point arc** as the **stable** half-court setup for that possession — no traditional low-post focal point anchoring the offense. If the set is only briefly wide before a different structure appears, label the **dominant** structure, not generically "5-out."

  **1-4 flat / high ball screen (or high PnR):** **One** initiator with the ball (top or wing entry) and **four** teammates **spaced across the perimeter** (wings, corners, arc — a **flat / spread** look relative to the paint), with the **primary on-ball screen at or above the free-throw line extended** toward the arc. This is **NOT** the same label as Horns (no required dual elbow anchors). **Critical:** Do **not** count these possessions **only** under **"5-out motion"** with a NOTE about a screen — give **this** structure its **own ACTION line** and **COUNT** when it is the main half-court look.

  **Horns / Horns DHO:** (see below — unchanged meaning)

HORNS vs GENERIC SPREAD:
  Label **Horns** (or **Horns / DHO**) when you see the **common Horns shape**: two elbow (or high-post) anchors, ball started by a guard at the top, screening/handoff action involving the elbow players—not merely "five players spaced."
  Do **not** call that package **only** "5-out motion." You may log a **second** ACTION line for perimeter spacing within the same possession if needed, but Horns deserves its own **COUNT** when that structure is visible.

ANTI-BUCKETING (mandatory):
  It is **forbidden** to use a fat **ACTION: 5-out motion** row to **absorb** possessions whose **dominant** structure was **Horns**, **1-4 flat / high PnR**, or **distinct motion continuity** documented elsewhere — unless every possession in that COUNT **actually** satisfies **5-out geometry** above. When a possession starts spaced then becomes a clear high pick-and-roll / flat entry, classify by the **half-court family** (**1-4 flat / high ball screen**), not vague "spread."

MULTIPLE BALL SCREENS IN ONE POSSESSION:
  Count the **primary** initiating structure once for the ACTION **COUNT**. Additional picks in the same trip → mention in **NOTES** ("second screen," "counter") unless a second distinct tactical entry is visibly a new set restart.

HALF-COURT OFFENSIVE LABELING (scouted team on offense):
  Use standard coaching vocabulary. When you can see a named structure, use a **specific** label — do **not** default everything to generic "5-out motion" or "spread PnR" if a tighter name fits.
  Prefer separate ACTION lines when these are visibly distinct in this segment:
    • Horns / Horns DHO (two elbow anchors — see above)
    • **1-4 flat / high pick-and-roll** or **high ball-screen series** (canonical geometry above)
    • 4-out 1-in, motion, pass-and-cut continuity, or canonical **5-out** spacing (only **5-out** when all five match the canonical definition above)
    • Transition / early offense (own basket break — see counting rules below)
  If you are unsure between two labels, describe the frame (e.g. "two bigs at elbows, guard initiates from top") and pick the best match, or flag uncertainty.

REACTIVE VS OPPONENT ZONE (offense — tagging):
  When the possession is **primarily an answer to opponent zone** (e.g. two guards high vs a 1-2-2 shell, 2-2-1 / "guards up," overload to a short corner, repeated **attacks to the middle of the zone** after the defense has shown a zone shell), keep your ACTION label honest (often still "1-4 flat / high ball screen" or "motion") but add to **NOTES** the exact token **`REACTIVE-VS-ZONE`** plus one short cue (e.g. "vs 1-2-2"). This is **not** their default half-court identity — it is a counter look. Omit the tag only if you truly cannot tell man from zone.

TRANSITION COUNT (strict):
  Count **Transition / early offense** only when the scouted team **clearly pushes to attack** before the defense sets — e.g. after a steal, long rebound, or clear outlet with numbers, and the possession **starts** in first ~6–8 seconds of the shot clock or equivalent hurry-up pace.
  After a **made basket** by the opponent, a slow dribble-up or casual reversal is **not** transition unless they **attack quickly** with a pass ahead or sprint clearly intended to score early. When in doubt, log as half-court and flag under FLAGGED.

FAST BRING-UP ≠ TRANSITION (same segment — both matter):
  **Transition** counts only the strict definition above.
  Separately observe **fast pace / hurried advance** where the defense **gets matched** and the offense runs a **normal half-court set** (often a quick entry pass then **late shot clock or organized action**). **Do not** add those possessions to Transition **COUNT** — describe them in **OFFENSIVE TEMPO SUMMARY** below so synthesis can praise pace without inflating transition stats.
  A **quick three** attempted after the defense has **organized** → usually **half-court** tempo, **not** transition unless the shot was clearly in the **immediate early-offense strike** window before matchup.

OPPONENT DEFENSE (while scouted team has the ball):
  If the opponent shows a **zone shell** — e.g. flat line across the lane, two guards high at the free-throw line (1-2-2 look), three across the paint (2-3), corners and wing filled with almost no man chasing through screens — name **zone** and the type if you can (1-2-2, 2-3, 3-2) or write **"zone (type uncertain)"**.
  Note how the scouted team attacked it (overload, middle drive, quick three, set play). If you only see zone for one or two possessions, still log it with count and flag small sample.

The video segment may be long; account for the full runtime from minute {start_min} through {end_min} — do not stop after only the first few minutes unless the video truly contains no further play.

Output your observations in this exact structure. Use the headers exactly as written.
Every section is required. If nothing was observed for a section, write "None observed in this segment."

=== CHUNK {chunk_index} OBSERVATION LOG ===
Segment: minutes {start_min}–{end_min} (approximately)
Possessions observed: [total offensive possessions for each team in this segment]

--- OFFENSIVE ACTIONS (Team being scouted) ---
For each offensive action observed, document:
  ACTION: [name — see labeling rules above; examples: "Horns / Horns DHO", "1-4 flat / high ball screen", "high pick-and-roll",
           "4-out 1-in / motion", "5-out motion", "transition / early offense", "BLOB quick hitter", "SLOB", etc.]
  COUNT: [exact number of times this action was run in this segment]
  PLAYERS: [jersey numbers and **exact roster names** of initiators and key participants — scouted team only]
  OUTCOME: [success rate in this segment — how many produced good shots, scores, turnovers, stalls]
  NOTES: [anything unusual — counters off the action, situational use, variation observed]

List every distinct action observed more than once.
Single-occurrence actions: list at the end under "SINGLE-OCCURRENCE ACTIONS" with a one-line description.
**Outbound / inbound formations:** Sweep stoppages for **BLOB/SLOB** (baseline or sideline). Log each distinct **formation** (4-across, stack, elbow popper, etc.) — repeat formations get a COUNT ≥ 2 in OFFENSIVE ACTIONS where possible.

--- OFFENSIVE TEMPO SUMMARY (THIS SEGMENT ONLY) ---
  Strict transition possessions (COUNT per rules above): [integer]
  Fast ball advance → settled half-court (defense generally matched — **NOT** counted as transition above): [short frequency / examples]
  Segment pace feel: [slow / moderate / fast]

--- DEFENSIVE SCHEME (Team being scouted, on defense) ---
  BASE DEFENSE: [man-to-man / zone type / press — be specific]
  SCHEME CHANGES: [did they change defenses during this segment? when? what triggered it?]
  **Defended opponent ball screens (scouted team on D) — quantify first:**
    **Opponent ball-screen possessions evaluable this segment:** N = [integer; 0 if none / none on film]
    If N ≥ 1, describe coverage using **two layers** (same clip can combine):
      • **BIG (screen defender — typically the scouted big):** [drop / show / hard hedge / switch / trap / ICE-style attach / unclear]
      • **BALL HANDLER’S DEFENDER:** [go over / under / ICE / switch / fight-through / trail / unclear]
    **Switch** applies only if defenders **exchange matchups onto new offensive players.** A guard contesting a pull-up after fighting over — while the big stays back — is **not** automatically "switch;" use **mixed** or name **drop + contest** accurately.
    If N < 4, append: **`thin sample in this segment — do not infer full-game primary coverage from this chunk alone.`**
  If the opponent ran **few or no** ball screens in this segment, write **N=0** explicitly — do not invent identity.
  COVERAGE CHANGES: [did ball screen coverage change? on which players or in which situations?]
  TRANSITION DEFENSE: [how do they get back? who is their primary back-defender?]
  NOTABLE MOMENTS: [specific defensive stops or breakdowns worth flagging — jersey numbers]
  OPPONENT STANDOUTS (vs scouted D): [only **opponent #[N]** format, optional (announcer "..."). **Mandatory content rule:** If any **opponent #[N]** in this segment shows **multiple** instances of **self-created offense** — off-the-dribble pull-ups, blow-bys creating separation for scores/FT — you **must** list them here with **opponent #[N]** and one-line factual evidence (**not** vague "hot hand"). If none qualify, write **"None standout this segment."** Never invent opponent full names per roster rules above.]

--- INDIVIDUAL PLAYER OBSERVATIONS ---
For each player who appeared in this segment, document observations (rostered scouted team only):
  #[JERSEY] [EXACT ROSTER NAME]:
    OFFENSE: [what they did — actions, tendencies, shots taken, results]
    DEFENSE: [how they defended — matchup, quality, breakdowns]
    COUNT: [approximately how many possessions they were on the floor]

Only include players with 3+ observable possessions. Skip players with minimal activity.

--- SCORE AND GAME CONTEXT ---
  Score at start of segment: [if determinable — else "not legible"]
  Score at end of segment: [if determinable — else "not legible"]
  **Score sources consulted this segment** (tick all that influenced your numbers): [broadcast bug / arena scoreboard (pan or fixed) / announcer / none legible — **explain**]
  If the on-screen score bug **jumps incorrectly**, freezes, or conflicts with **arena board** or announcer — note it under FLAGGED OBSERVATIONS; prefer the source that matches **plays you clearly see**.
  **End-of-game / final score in this clip:** Different uploads differ (no FINAL graphic may exist — phone film, scout cut, missing last minute).
    • If you see **definitive** end-of-game evidence (e.g. "FINAL" full-screen graphic common on broadcasts, legible horn-time scoreboard totals, definitive announcer "final Score X–Y" **and** visuals align), record it.
    • If the segment **does not contain** credible end-game proof, write **`final score not established in this segment`** — never guess totals for the column.
    • Mid-game chunks: **never** label a hypothetical "official final" inferred only from flaky tickers.
  Game situation notes: [was either team protecting a lead? pressing? fouling intentionally?]
  Tempo notes: [pace — may reference OFFENSIVE TEMPO SUMMARY]

--- SUBSTITUTIONS, LINEUPS, AND AVAILABILITY ---
  Notable subs, injury timeouts, cramping, return-to-play, or lineup changes that affect scouting. Use **only** roster jersey numbers and **exact roster names** for players entering and leaving. If you are unsure who came in, write "substitution occurred — inbound jersey not confirmed" and FLAG.

--- FLAGGED OBSERVATIONS ---
List anything in this segment that seems important but you are uncertain about:
  - Plays or actions you could not confidently identify
  - Player jersey numbers you could not confirm from the roster (scouted team) or from video (opponent)
  - Opponent zone type or coverage you only partially saw
  - Game situations that seem unusual or that changed how both teams played
  - Any count you are not confident in (state your uncertainty — e.g., "I counted 4 but may have missed 1")
  - Ball-screen defense: if you had very few opponent PnR possessions to watch, say "thin sample — do not treat as full-game primary coverage"

Be honest about uncertainty. An uncertain count flagged here is more useful than a confident
wrong count that propagates into the synthesis.
=== END CHUNK {chunk_index} LOG ===
```

**Injection note:** `{chunk_index}`, `{total_chunks}`, `{start_min}`, `{end_min}`, and `{roster}` are
filled programmatically before the prompt is sent. The worker computes start/end minutes
from `film_chunks.chunk_index` and `film_chunks.duration_seconds`. `{roster}` is rendered by
`services/roster_format.py::format_roster_for_prompt(team_id)`.

---

### STAGE 2 — SYNTHESIS PROMPT

**File:** `backend/prompts/chunk_synthesis.txt`

**Canonical text (2026-05-19):** Live **`VERSION: v1.6`** in **`chunk_synthesis.txt`**. Fenced body below is a verbatim mirror as of this update. The `.txt` file is the source of truth — bump the mirror in the same PR as any `.txt` edit.

```
VERSION: v1.6
CHANGELOG:
  v1.6 — Final score ladder + insufficient; mandatory segment breakdown math per inventory line; forbidden [CONFIRMED] defended PnR under small N / chunk conflict → mixed; tempo: strict transition sum + pace from chunk summaries; standout operational definition (OTD/separation).
  v1.5 — Reactive zone-offense split: do not fold REACTIVE-VS-ZONE possessions into base Horns/1-4/motion totals without a sub-count; thin-sample discipline for scouted team's defensive PnR coverage when N is tiny.
  v1.4 — No invented opponent names; Horns must not merge into 5-out; zone section mandatory sweep; inventory ranking for prep structure; late-game sub cross-check; transition vs half-court reconciliation.
  v1.3 — Final score reconciliation; defensive PnR coverage confidence discipline; separate half-court inventory (Horns / 1-4 flat vs generic 5-out); opponent zone + problem player; synthesis flags for scoreboard errors.
  v1.2 — Paired with `chunk_extraction` for `film_analysis_cache` key (see `services/prompt_versions.py`).
  v1.0 — Initial version.
---
You are synthesizing multiple observation logs from consecutive segments of a basketball game
into a single, unified full-game intelligence document.

You will receive:
1. Observation logs from {total_chunks} consecutive game segments, covering the full game.
2. The complete roster of the team being scouted.

Your job is to resolve inconsistencies, aggregate counts, identify game-long patterns, and
produce a structured full-game intelligence document. This document will be used as the
foundation for a professional scouting report. Errors here propagate into every section
of the report. Accuracy is the only priority.

SYNTHESIS RULES — READ BEFORE PRODUCING OUTPUT:

Rule 1 — AGGREGATE COUNTS EXACTLY.
Count every occurrence of each action across all segments and report the total.
For **every line** under **OFFENSE: SET AND ACTION INVENTORY**, you MUST print **explicit arithmetic**, e.g.
  `Segment breakdown (show work): chunk0:11 + chunk1:9 + chunk2:4 + chunk3:0 = Total 24`
before **Success rate.** Same **show work** for **transition** tally and defended-PnR **N** rollup in defensive coverage. Silent totals without sums are unacceptable.
Do not re-label a possession mid-count — if a chunk called it Horns and another called it "5-out" for what reads like the **same** elbow / horns setup, **prefer Horns** in reconciliation and explain; do not silently fold Horns into "spread."

Rule 1b — **TOP INVENTORY AUDIT BEFORE ORDERING:**
Re-scan all chunk ACTIONS for **`1-4 flat`**, **`high ball screen`**, **`high PnR`**, **`Horns`**. If chunks buried many of those rows under **generic "5-out"** only because of **ANTI-BUCKETING** failure in upstream logs, correct in synthesis: **pull** those occurrences into **`1-4 flat / high ball screen`** and **Horns** lines when descriptive evidence supports — **FLAG** **`Chunk bucketing repaired in synthesis`** with confidence **Medium** unless chunk text is explicit—prefer **calling out contradiction** vs inventing unseen possessions.

Rule 2 — RECONCILE VOCABULARY BEFORE COUNTING.
Different chunk logs may use different names for the same action. Before aggregating,
determine whether two named actions are the same action described differently.

Half-court structure (scouted offense): **Do not** merge visibly different families into one bucket
just because they are all "perimeter-oriented."
  • **Horns / Horns DHO** — keep **separate** from generic **5-out motion**. If chunk text mentions elbows, horns, DHO from elbow, two high-post anchors, etc., that inventory line is **Horns**, not 5-out.
  • **1-4 flat / high PnR** — handler on top, four flat, ball screen at or above the arc — keep separate from vague "spread" unless chunks prove identical structure.
  • **4-out 1-in / motion** / **5-out** — only when spacing matches those definitions.
  • **Transition / early offense** — separate from half-court; if chunks over-count transition per the chunk prompt, cap or adjust using narrative consistency and FLAG in SYNTHESIS FLAGS.
  • **Reactive zone offense** — when chunk **NOTES** contain **`REACTIVE-VS-ZONE`** (or equivalent phrasing: "against zone," "middle of the zone," "2-2-1," "guards up vs 1-2-2"), those possessions are **responses to opponent zone**, not proof of a new base half-court package. In **OFFENSE: VS ZONE AND OPPONENT DEFENSIVE LOOKS**, add a sub-block **Reactive zone-offense possessions:** with count + short evidence by segment. In **OFFENSE: SET AND ACTION INVENTORY**, either **exclude** those possessions from the headline totals for Horns / 1-4 / motion **or** show **base vs reactive** in parentheses (e.g. "Total: 12 (9 base half-court + 3 REACTIVE-VS-ZONE)"). Do not report only the merged total without acknowledging the split when chunks flagged reactive play.

Before finalizing the **OFFENSE: SET AND ACTION INVENTORY** order, scan **all** chunk text for
the strings **Horns**, **elbow**, **1-4**, **high ball**, **flat**. If Horns and 1-4 / high PnR each have meaningful counts, **neither** may be buried below a generic "5-out" line unless chunk evidence shows 5-out truly had higher totals.

**Spain PnR, Flex, Iverson, Princeton, elevator** — do not introduce these labels unless chunk logs **explicitly** describe them. If chunks do not mention them, do not add them from general basketball knowledge.

Rule 3 — PRESERVE TIMELINE INFORMATION.
If a team's scheme, coverage, or personnel usage changed during the game, document when
and why.

Rule 4 — HANDLE CONTRADICTIONS EXPLICITLY.
If two chunk logs report conflicting observations about the same action or player, do not
silently choose one. Flag the contradiction, state what each chunk logged, and state your
best resolution with your confidence level.

Rule 5 — SURFACE SINGLE-GAME SIGNALS VS CONFIRMED PATTERNS.
Tag observations with confidence:
  [CONFIRMED] — observed in 3+ segments **or** 8+ logged occurrences of the same discrete behavior
  [LIKELY]    — observed in 2 segments **or** 4–7 occurrences
  [SINGLE GAME SIGNAL] — observed once or in only one segment. Possible tendency. Not confirmed.

**Defensive ball-screen coverage (scouted team vs opponent PnR):** Be conservative.
First sum **N_total** implied across chunks (**opponent** on-ball picks the scouted team defended). If chunks give **thin sample**, say so.
• **[CONFIRMED]** for a **single** umbrella label (**switch**, **drop**, etc.) as **team primary coverage** is **FORBIDDEN** unless **either** ≥ **8** evaluable defended PnR possessions support it **OR** ≥ **three** chunks independently describe consistent **BIG-level** technique (same family).
• If **N_total < 4**, cap at **[LIKELY]** or **[SINGLE GAME SIGNAL]** and write **thin sample — insufficient to declare full-game primary coverage.**
• If chunks **contradict** (e.g. chunk A drop/contain vibe, chunk B switch narrative) without clear timeline proof, **`Primary coverage:` `mixed`** + explicit contradiction **FLAG—do not synthesize fake smooth progression.**

Rule 6 — FINAL SCORE AND GAME RESULT (multi-source uploads).
Uploads vary: broadcast FINAL graphic, horn-time arena scoreboard pan, phone film with weak bug, scout clip missing ending.
**Prefer evidence in this ladder** (stop at best available):
  1) **Definitive end-of-video / end-of-period evidence** aligned across picture + sound ("FINAL" style graphic typical on broadcasts, **legible** scoreboard totals at horn, unmistakable definitive announcer finals **and** coherent with last plays).
  2) Clear **arena scoreboard** read late.
  3) Reliable **consistent** ticker at **segment end before cut** ONLY if nothing better—and **still** reconcile with plausible event flow.

**Insufficient / honest unknown:** Write exactly
`Final score (reconciled): insufficient observation — end-of-game not shown clearly or sources conflict unresolved`
**Never guess** a **final score** from mid-game glitchy bugs. Prefer **later** chronological chunk over earlier if conflict (legacy rule). Explain every score conflict under **SYNTHESIS FLAGS.**

Rule 7 — OPPONENT ZONE AND STANDOUTS.
Before writing **"None clearly observed"** in **OFFENSE: VS ZONE**, search all chunk logs for:
**zone**, **2-3**, **1-2-2**, **2-2-1**, **overload**, **middle of the zone**, **against zone.**
If any appear, summarize with segment evidence. Conflicting small-sample notes still belong here, not silence.

**Opponent standout (problem matchup):**
  • List **opponent #[N] only** for identity. Trigger: repeated **self-created offense** — pull-ups, separation for scores/FT vs scouted D — cite evidence from chunk logs (game clock if present in text). **Never** label with vague "hot hand" alone.
  • If chunk **OPPONENT STANDOUTS** or **NOTABLE MOMENTS** support a **problem opponent #[N]** and you wrote **none**, reopen those sections — omission is failure.
  • You may add **(announcer said "...")** if chunks quoted it — **never** invent full names or verify opponent names not in chunk text.
  • Do not fill opponent names from general knowledge (e.g. famous prep players) — that is a hard failure mode.

Rule 8 — ROSTER, SUBS, AND SPELLING.
Scouted-team names must match the roster **exactly** character-for-character everywhere in the document.
When **SUBSTITUTIONS, LINEUPS, AND AVAILABILITY** sections mention cramps or late subs, **reconcile who entered** across chunks. If chunk A says #5 entered and chunk B says #10 for the same stoppage, treat it as a contradiction — resolve from later/clearer chunk or FLAG.

Rule 9 — NEVER INVENT.
If the chunk logs do not contain enough information to answer a question, say so.

---

OUTPUT FORMAT — produce these exact sections in this exact order:

=== FULL-GAME INTELLIGENCE DOCUMENT ===
Team: [name from roster context]
Total segments analyzed: {total_chunks}
Total possessions logged: [sum scouted-team possessions from chunk headers if present; if chunks disagree, show sum and FLAG]
Opponent possessions: [sum if logged per chunk; otherwise "not logged 1-for-1 in chunk headers — insufficient"]

Final score (reconciled): [Winning Team **nn** — Losing Team **mm** winner + margin **OR** verbatim `insufficient observation — ...` per Rule 6]

--- OFFENSE: SET AND ACTION INVENTORY ---
[List every offensive action — see Rule 2. Horns and 1-4 flat / high PnR must appear as their own lines when chunk evidence supports them, not only inside a generic spread label.]

  [ACTION NAME] [CONFIDENCE TAG]
  Total occurrences: [exact count] — **must equal** the sum line below (no mismatch).
  **Segment breakdown (show work):** [chunk sums like `chunk0:X + chunk1:Y + ... = Total`]
  Primary initiators: [jersey numbers and **exact roster names**]
  Primary screeners/participants: [jersey numbers and **exact roster names**]
  Typical floor position: [where on court it initiates]
  Success rate: [scores / fouls / TO relative to runs — honest]
  Key counter: [if observed]
  Reconciliation note: [if vocabulary was unified across chunks, state it here — or why kept separate]

Order by total occurrences (descending). Their most-used action appears first.

--- OFFENSE: VS ZONE AND OPPONENT DEFENSIVE LOOKS ---
  Opponent zone: [types / evidence / small sample flags — "None clearly observed" **only** after Rule 7 search finds nothing]
  How the scouted team attacked it: [sets or principles, or insufficient observation]

--- OFFENSE: TEMPO AND PACE ---
  **Strict transition (early offense)** — sum ONLY per chunk extraction strict rule; include **segment breakdown arithmetic** `(e.g. chunks 1–4 sums = total)`.
  **Fast pace without transition bucket** — summarize from chunks' **OFFENSIVE TEMPO SUMMARY**: hurry-up advances that **settled** half-court; praise pace without stealing transition tally.
  Push vs half-court feel: [narrative + reconcile if summed transition contradicts sheer possession volumes — FLAG disconnects]
  Average time to half-court action initiation: [fast / moderate / deliberate]
  Pace changes: [when + evidence]

--- OFFENSE: OUT-OF-BOUNDS SETS ---
  List every distinct BLOB/SLOB **formation** or repeating look observed (stack, 4-across, box, etc.). Same inventory-style lines as above when count > 1.
  If none observed: "No out-of-bounds sets with repeating structure observed."

--- OFFENSE: LATE-GAME (final 8 minutes of close games) ---
  Primary isolation player: [jersey number and **exact roster name**, with occurrence count]
  Shot clock offense (under 8 seconds): [what they run and who runs it]
  Scheme changes when protecting lead: [if observed]
  Scheme changes when trailing: [if observed]
  Notable availability / lineup: [only from chunk SUBSTITUTIONS — cramps / key sub; **exact** jersey numbers]

--- DEFENSE: BASE SCHEME ---
  Primary defense: [man / zone type / press]
  Percentage of possessions: [approximate]
  Scheme changes: [timeline]
  Transition defense: [quality]

--- DEFENSE: BALL SCREEN COVERAGE ---
  **Opponent defended ball-screen possessions (evaluable cumulative N across chunks — show arithmetic):** N_total = [...]
  Primary coverage narrative: [**drop /** **hedge /** **switch /** **ICE /** **blitz /** **mixed`] [CONFIDENCE TAG per tightened Rule above]
  Evidence summary: [which segments quoted N; cite thin sample verbatim if totals <4 — **Forbidden** inflate to [CONFIRMED] primary-read team identity]
  Coverage variations: [detail]
  Coverage timeline: [timeline]
  Execution quality: [breakdowns — tie to opponent # if chunks did]

--- DEFENSE: OPPONENT STANDOUT VS SCOUTED TEAM ---
  Problem matchup / opponent standout(s): [**opponent #[N]** only, plus factual notes from chunks; optional announcer quote in parentheses — **no invented full names**]
  Confidence: [CONFIRMED / LIKELY / SINGLE GAME SIGNAL] with justification

--- DEFENSE: INDIVIDUAL TENDENCIES ---
For each player with significant defensive responsibilities:
  #[JERSEY] [EXACT ROSTER NAME]:
    Primary assignment: [who or what they guarded — opponent # if for a matchup]
    On-ball quality: [evidence]
    Help activity: [examples]
    Identified weakness: [what beats them; **opponent #** if chunks tie a scorer to it]
    Confidence: [CONFIRMED / LIKELY / SINGLE GAME SIGNAL]

--- INDIVIDUAL PLAYER CONSOLIDATED PROFILES ---
For each player with 10+ observed possessions across all segments:
  #[JERSEY] [EXACT ROSTER NAME]:
    Total possessions observed: [sum]
    Offensive role: [specific, with counts]
    Scoring zones: [evidence]
    Dominant hand: [evidence or insufficient data]
    Key tendencies: [tagged]
    Defensive assignment: [summary]
    Defensive vulnerability: [summary]

--- SYNTHESIS FLAGS ---
  - Vocabulary / count judgment calls
  - Contradictions (scores, subs, coverage)
  - **Never** list invented opponent identities here as if confirmed — only "model would have guessed X — rejected per Rule 7/9"
  - Scoreboard / clock issues (Rule 6)

=== END FULL-GAME INTELLIGENCE DOCUMENT ===
```

---

### HOW SECTIONS 1-4 CONSUME THE SYNTHESIS DOCUMENT

The synthesis document is prepended to the Gemini context cache before sections 1-4 fire.
Each section prompt is not modified — sections 1-4 receive the same prompts as documented below.
The synthesis document is visible to Gemini as structured prior knowledge.

**Instruction prepended to every section 1-4 call:**

```
A full-game intelligence document has been pre-computed from all film segments and is provided
below. This document contains reconciled action counts, confirmed player tendencies, and flagged
uncertainties. Use it as your primary reference for counts, frequencies, and player attributions.
You are also watching the complete game film directly. If you observe something in the film that
contradicts the intelligence document, trust the film and note the discrepancy.
Items tagged [SINGLE GAME SIGNAL] in the document should be reported in your section with the
same uncertainty — do not present them as confirmed tendencies.
Items tagged [CONFIRMED] are reliable and can be stated with confidence.

--- FULL-GAME INTELLIGENCE DOCUMENT ---
{synthesis_document}
--- END INTELLIGENCE DOCUMENT ---

{section_prompt}
```

This means: the synthesis document informs sections 1-4 but does not override the video.
Gemini watches the film and has the synthesis as a structured aid. The two inputs check each other.
If the synthesis says 9 Horns sets and Gemini watching the film sees 11, the section output
notes the discrepancy. That discrepancy becomes a correction signal for the extraction prompt.

---

### FAILURE HANDLING

**If a chunk extraction fails:**
Mark that chunk's extraction as failed in `film_chunks.extraction_status`.
The synthesis prompt receives the available extractions and is told which chunk is missing:
"WARNING: Chunk {index} extraction failed. Segment covering minutes {start}–{end} has no
extraction log. Your synthesis should note this gap explicitly."
The synthesis proceeds on available data. The missing segment is flagged in the synthesis document.
Sections 1-4 are notified via the intelligence document header.

**If the synthesis call fails:**
Retry 3 times (same policy as section tasks). On third failure: sections 1-4 run without
the synthesis document, using only the raw video and the instruction:
"Note: full-game synthesis was unavailable. Derive all counts and tendencies directly from the film."
This is a graceful degradation — the report is generated, not blocked.
The failure is logged to `dead_letter_tasks` and surfaces in Datadog as `tex.synthesis.failed`.

**If the synthesis document contains a flag that affects a section:**
Sections 1-4 are responsible for surfacing synthesis flags in their output. The section prompt
instructs Gemini to report flagged items with uncertainty. Tommy sees the flag in the report.
It becomes a correction target: was the flag legitimate uncertainty or a synthesis error?
Both outcomes are valuable training signals.

---

*Last updated: 2026-05-19 — Prompt 0 disk versions **v1.6**; PROMPTS.md §STAGE 1/2 fences re-mirrored verbatim to v1.6 bodies; canonical text stays in **`backend/prompts/*.txt`** — bump the mirror in the same PR as any `.txt` edit.*
*Production Prompt 0 pair: **`chunk_extraction` v1.6 + `chunk_synthesis` v1.6** (must stay aligned unless intentionally split with `prompt_versions.py` composite key).*
*Continued post-eval iteration is tracked in GitHub Issue #28 — bodies above are canonical until that issue closes.*
*This is the highest-priority prompt to iterate on. Accuracy here determines accuracy everywhere.*

---

## SECTION 1 — OFFENSIVE SETS

**File:** `backend/prompts/offensive_sets.txt`
**Model:** Gemini 2.5 Pro
**Input:** Context cache (video + roster)
**Output:** Full offensive scouting section

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball scout analyzing game film for a coaching staff preparing a scouting report.
Your output will be printed and used on a clipboard during a live game. Every word must earn its place.

Analyze the complete game film provided and produce the OFFENSIVE SETS section of the scouting report.
Use the roster provided in context to attribute every action to specific players by jersey number and name.

WHAT TO IDENTIFY AND DOCUMENT:

1. PRIMARY HALF-COURT OFFENSE
   Identify their primary half-court offensive system. Is it motion-based, set-based, or a hybrid?
   If they run named sets: identify the set (Horns, Spain PnR, Floppy, DHO Series, Pistol, Elevator,
   Zipper, Blob/Slob, 5-Out motion, etc.). Name it using standard coaching terminology.
   For each primary set:
   - Which players initiate it (jersey number and name)
   - What triggers the set (signal, floor position, personnel grouping, or game situation)
   - Exactly how it develops — screen actions, cuts, reads in order
   - Primary options (first action) and secondary options (counter off the first action)
   - How often they ran it (count of possessions — be precise, not approximate)
   - Success rate: did it produce a good shot, a turnover, or a stall?

2. SECONDARY ACTIONS
   Document every recurring offensive action observed more than 3 times:
   - DHO (dribble handoff) — who initiates, who receives, direction
   - Pin-down screens — screener, cutter, which side of floor
   - Flare screens — who for, game situation (typically late shot clock)
   - Transition sets — how they push in transition, primary ball handler, decision makers
   - Early offense — what they run before the defense sets

3. OUT-OF-BOUNDS PLAYS
   Document every baseline and sideline out-of-bounds set observed:
   - Name or describe the action
   - Who the primary target is
   - What makes it work

4. LATE-GAME OFFENSE
   How do they score in the last 4 minutes of a close game?
   - Primary isolation player (jersey number and name)
   - Shot clock situations: what do they run with under 8 seconds?
   - Foul-drawing tendencies

5. TEMPO AND PACE
   - Do they push in transition or set up half-court?
   - Average time before initiating half-court action (fast, moderate, deliberate)
   - Do they change pace situationally (ahead vs behind, by opponent defense type)?

OUTPUT FORMAT:
Write in complete sentences organized under the exact headings above. Use coaching vocabulary.
Do not use bullet points for the main analysis — write in paragraphs that read like a scout's report.
Bullet points are acceptable only for listing out-of-bounds sets or a quick-reference set inventory.
Be specific. "#3 Williams initiates the Horns action from the top every time — his tell is a right-hand
signal to the bigs before the ball crosses half court" is useful. "They run some sets" is not.
Count occurrences. If you observed a set 11 times, write 11. If you counted approximately 8-10, write that
and note the uncertainty. Do not round to the nearest 5 or fabricate precision you do not have.
Attribute everything to jersey numbers and names. A coach watching this film knows every player by number.
```

---

## SECTION 2 — DEFENSIVE SCHEMES

**File:** `backend/prompts/defensive_schemes.txt`
**Model:** Gemini 2.5 Pro
**Input:** Context cache (video + roster)
**Output:** Full defensive scouting section

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball scout analyzing game film for a coaching staff preparing a scouting report.
Your output will be printed and used on a clipboard during a live game. Every word must earn its place.

Analyze the complete game film provided and produce the DEFENSIVE SCHEMES section of the scouting report.
Use the roster provided in context to attribute tendencies to specific players by jersey number and name.

WHAT TO IDENTIFY AND DOCUMENT:

1. PRIMARY HALF-COURT DEFENSE
   What is their base defense? Man-to-man, zone, or a mix?
   If man-to-man:
   - Is it pressure man, contain man, or help-heavy?
   - How do they defend the ball handler (on-ball pressure level)?
   - Where do they position off-ball defenders (deny, sag, gap)?
   - How do they guard the post (front, 3/4, behind)?

   If zone:
   - Type: 2-3, 3-2, 1-3-1, matchup zone, or other
   - What triggers them into zone? (opponent personnel, game situation, score)
   - Identify the gaps and dead spots in their zone alignment
   - How do they rotate? Who is responsible for corner coverage?

   If they mix:
   - What triggers the switch? (score differential, personnel, opposing team's offense)
   - What percentage of possessions did you observe each defense?

2. TRANSITION DEFENSE
   - Do they sprint back or slow-retreat?
   - Who is their primary transition stopper (jersey number)?
   - Do they have an identified runner who stays back?
   - How many transition baskets did the opponent generate against them?

3. DEFENSIVE ROTATIONS AND HELP PRINCIPLES
   - Are they help-and-recover or pack-the-paint?
   - How do they defend skip passes — are corners covered?
   - How do they respond to dribble penetration — do they tag the roller or protect the corner?
   - Who is their best on-ball defender? Identify by jersey number.
   - Who is their weakest defensive player? Identify by jersey number. Be specific about what they cannot guard.

4. PRESS / TRAPPING
   - Do they press? Full court, half court, or neither?
   - What triggers a press or trap? (inbound plays, after made free throws, specific game situations)
   - How do they rotate if the press is broken?
   - What is the best action to attack it?

5. LATE-GAME DEFENSE
   - Do they foul intentionally when trailing? At what score/time threshold?
   - Do they switch to a different defense when protecting a lead?
   - Who do they send to foul? (worst free throw shooter on the opposing team, or random?)

6. PERSONNEL DEFENSIVE MATCHUPS
   For each player on the opposing roster: who does this team prefer to guard them with?
   Note mismatches — situations where a defender is clearly overmatched or advantaged.

OUTPUT FORMAT:
Write in complete sentences under the exact headings above. Coaching vocabulary throughout.
Be blunt about weaknesses. "Their zone leaves the short corner completely unguarded on skip passes — this
happened 7 times and produced 3 open looks" is the correct level of specificity.
Attribute observations to jersey numbers. If #41 cannot guard in space, say #41 cannot guard in space.
```

---

## SECTION 3 — PICK AND ROLL COVERAGE

**File:** `backend/prompts/pnr_coverage.txt`
**Model:** Gemini 2.5 Pro
**Input:** Context cache (video + roster)
**Output:** Full PnR coverage section

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball scout analyzing game film for a coaching staff preparing a scouting report.
Your output will be printed and used on a clipboard during a live game. Every word must earn its place.

Analyze the complete game film provided and produce the PICK AND ROLL COVERAGE section of the scouting report.
This section documents both how this team DEFENDS pick and roll and how they USE pick and roll offensively.
Use the roster in context to attribute every tendency to specific players by jersey number and name.

PART A — HOW THEY DEFEND PICK AND ROLL (as the defense)

1. BASE BALL SCREEN COVERAGE
   What is their primary coverage on ball screens?
   - Drop: ball defender goes under, big stays at the level of the screen or lower
   - Hedge / Hard Hedge: big jumps out aggressively to cut off the ball handler
   - Switch: ball defender and big trade assignments
   - ICE / Blue: ball defender forces ball handler away from the screen, toward sideline
   - Blitz / Trap: ball defender and big double-team the ball handler at the point of the screen
   - Show: big shows high but recovers — softer than a hedge

   State the primary coverage and the secondary coverage (if they mix).

2. COVERAGE TRIGGERS — DOES IT CHANGE BASED ON PERSONNEL?
   Do they switch their coverage based on who is handling the ball or who is setting the screen?
   - Do they hedge on one handler but drop on another? Identify by jersey number.
   - Do they switch when a specific big sets the screen? Identify by jersey number.
   - Do they change coverage on the weak side vs strong side of the floor?

3. COVERAGE EXECUTION QUALITY
   How well do they actually execute their stated coverage?
   - If they drop: is the big staying low enough? Are they giving up pull-up jumpers?
   - If they hedge: is the recovery strong? Are they getting blown by on the closeout?
   - If they switch: are they creating mismatches you can target?
   Identify the specific breakdown point if their coverage has a consistent leak.

4. LATE-GAME COVERAGE CHANGES
   Do they change their ball screen coverage in the last 4 minutes of a close game?
   Many teams switch everything late. Note if this is the case and at what threshold.

PART B — HOW THEY USE PICK AND ROLL (as the offense)

5. PRIMARY BALL SCREEN ACTIONS
   - Who is the primary ball handler in PnR? (jersey number and name)
   - Who are the primary screen setters? (jersey number and name)
   - Where on the floor do they initiate PnR? (top, side, middle, corners)
   - Do they run more pick and roll (roll to rim) or pick and pop (shoot off the screen)?
   - How often? Count it.

6. BALL HANDLER READS
   When their ball handler comes off the screen, what is their first read?
   - Turn the corner and attack the rim?
   - Pull-up jumper at the screen level?
   - Throw it back to the screener rolling or popping?
   - Kick out to shooters in the corners?
   Identify which reads this specific ball handler prefers and how effective each is.

7. POP VS ROLL TENDENCIES
   For each screen setter: do they roll or pop? Are they a scoring threat either way?
   If they pop: range? Are they a legitimate three-point threat?
   If they roll: are they a lob threat, a finish-in-traffic threat, or neither?

OUTPUT FORMAT:
Write Part A and Part B under clearly labeled headers.
Use sub-headers for each numbered section above. Short paragraphs under each.
This section is often the most critical in the entire report — coaches use it every possession.
Precision matters more here than anywhere else. Vague coverage descriptions are useless at gametime.
"They hedge but #5 is slow to recover — the ball handler who is quick enough to beat #5 on the closeout
will get to the rim 6 out of 10 times" is useful. "They play hedge coverage" is not.
```

---

## SECTION 4 — INDIVIDUAL PLAYER PAGES

**File:** `backend/prompts/player_pages.txt`
**Model:** Gemini 2.5 Pro
**Input:** Context cache (video + roster)
**Output:** One profile section per rostered player

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball scout analyzing game film for a coaching staff preparing a scouting report.
Your output will be printed and used on a clipboard during a live game. Every word must earn its place.

Analyze the complete game film provided and produce the INDIVIDUAL PLAYER PROFILES section.
Every player on the roster must have a profile. If a player did not appear in the film, note "Did not appear in film — no data."
Use jersey numbers and names exactly as provided in the roster context.

For each player, produce a profile using this exact structure:

---
#[JERSEY NUMBER] [FULL NAME] | [POSITION if known]

OFFENSIVE PROFILE
Primary action: [Their most frequent and dangerous offensive action in one sentence]
Scoring zones: [Where on the floor they score most effectively — be specific about court location]
Ball handling: [Can they create off the dribble? Limited to catch-and-shoot? Somewhere between?]
Screen actions: [Do they use screens well? Set them well? Both? Neither?]
Tendencies:
  - [Specific tendency observed 3+ times — e.g., "Attacks left almost exclusively off DHO actions"]
  - [Additional tendency]
  - [Additional tendency — as many as observed, minimum 2 if player had significant minutes]

DEFENSIVE PROFILE
Primary assignment: [Who or what position they typically guard]
On-ball defense: [Pressure level, footwork quality, tendency to reach or gamble]
Help defense: [Are they active in help? Do they rotate? Do they tag rollers?]
Vulnerability: [Explicit weakness — what action or situation puts them in difficulty]

SCOUTING NOTE
[2-4 sentences. The most important thing a coach needs to know about this player going into the game.
This should be the thing that changes how the coaching staff prepares. Make it specific and actionable.]
---

Produce one complete profile for every player listed in the roster context.
Separate each profile with the --- delimiter on its own line.
Order profiles by jersey number (ascending).
Do not skip players. Do not merge players. One section per player.

If a player had limited minutes (< 5 possessions observed), shorten the profile and note the limited sample:
"Limited sample — appeared in approximately [X] possessions. Observations may not be representative."

Be direct about weaknesses. Hedging on a player's defensive liability helps nobody.
"#41 Hayes cannot guard in space — any pick and pop action directed at him will produce an open look.
He has no lateral quickness and tends to help off shooters prematurely" is the correct level of specificity.
```

---

## SECTION 5 — GAME PLAN

**File:** `backend/prompts/game_plan.txt`
**Model:** Gemini 2.5 Flash (fallback: Claude 3.5 Sonnet)
**Input:** Sections 1-4 text (no video)
**Output:** Full game plan section

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball strategist generating a game plan for a coaching staff based on a complete
scouting report of an upcoming opponent. The scouting report context provided contains a full analysis
of the opponent's offensive sets, defensive schemes, pick and roll coverage, and individual player profiles.

Your job is to translate that analysis into a specific, actionable game plan. Every recommendation must
be grounded in the scouting report context. Do not generate generic basketball advice. If a recommendation
cannot be tied directly to something observed in the film analysis, do not include it.

Produce the GAME PLAN section under these exact headings:

OFFENSIVE ATTACK PLAN

1. PRIMARY OFFENSIVE STRATEGY
   Based on this opponent's defensive scheme, what is the highest-percentage offensive approach?
   Identify the specific vulnerability in their defense and the specific action that exploits it.
   Example: "Their drop coverage on ball screens gives the ball handler the pull-up jumper at the
   screen level consistently. Make this the primary action every half-court possession."
   Be this specific. Name the action. Name the coverage. Name why it works against this team specifically.

2. TOP-3 ACTIONS TO RUN
   The three offensive sets or actions that should generate the most good looks against this defense.
   For each:
   - Name the action using standard terminology
   - Why it works against this specific team (tie to the scouting report)
   - How often to use it (primary, situational, or late-game only)

3. PLAYERS TO ATTACK
   Based on the player profiles, who are the defensive liabilities?
   For each identified mismatch target:
   - Jersey number and name of the liability
   - Exact action to run at them
   - What makes them vulnerable (from the player profile)

4. ACTIONS TO AVOID
   What does this defense take away well? What offensive approach will not work?
   Be specific — identify what they defend effectively and why running certain actions against
   them will be low-percentage.

DEFENSIVE GAME PLAN

5. HOW TO DEFEND THEIR OFFENSE
   Given their primary offensive sets identified in the scouting report:
   - What base defensive approach do you recommend and why?
   - Are there specific sets you must take away (their highest-frequency, highest-efficiency actions)?
   - What adjustments should the defense make to disrupt their primary actions?

6. BALL SCREEN COVERAGE RECOMMENDATION
   Given their PnR tendencies and personnel identified in the scouting report:
   - What coverage do you recommend on their primary ball screen actions?
   - Does this change based on which player has the ball or which big sets the screen?
   - Specific reasoning tied to the personnel profiles.

7. INDIVIDUAL MATCHUP ASSIGNMENTS
   Based on the player profiles: recommend defensive matchup assignments.
   Who should guard their primary scorer? Who should be hidden on defense?
   If there is a clear mismatch they will try to create, identify it and state how to deny it.

OUTPUT FORMAT:
Write under the exact headings above. Complete sentences and paragraphs. Coaching vocabulary.
Every recommendation must include "because" — the reason grounded in the scouting report.
"Run Horns for your primary ball handler because their drop coverage concedes the pull-up at the
screen level and they gave up 8 pull-up mid-range jumpers in the film" is correct.
"Run Horns" without the reason is incomplete.
This section is what the head coach reads before the game. It must be ready to use without edits.
```

---

## SECTION 6 — IN-GAME ADJUSTMENTS + PRACTICE PLAN

**File:** `backend/prompts/adjustments_practice.txt`
**Model:** Gemini 2.5 Flash (fallback: Claude 3.5 Sonnet)
**Input:** Sections 1-5 text (no video)
**Output:** Adjustments and practice plan section

```
VERSION: v1.0
CHANGELOG:
  v1.0 — Initial version.
---
You are an elite basketball strategist generating in-game adjustment protocols and a pre-game practice plan
for a coaching staff. You have access to the complete scouting report and game plan for an upcoming opponent.

Produce the IN-GAME ADJUSTMENTS AND PRACTICE PLAN section under these exact headings:

IN-GAME ADJUSTMENT TRIGGERS

Document specific triggers that should cause a coaching staff to adjust their game plan mid-game.
Each trigger must be grounded in the scouting report — a pattern, tendency, or vulnerability that was
observed in film and that the opponent may exploit or that TEX recommends attacking.

For each trigger, provide:
- TRIGGER: The observable in-game condition (score, their action, your failure)
- ADJUSTMENT: The specific change to make
- HOW TO EXECUTE: 1-2 sentences on what to tell the players

Format each as:

TRIGGER [number]:
  If: [Observable condition — e.g., "Their zone is holding you under 1.0 PPP for 4+ possessions"]
  Then: [Adjustment — e.g., "Attack the short corner with your best mid-range shooter (#3). Their
         zone leaves the short corner completely unguarded on skip passes — exploit this immediately."]
  Tell your team: [Plain language instruction for a timeout huddle]

Provide a minimum of 6 triggers. Include:
  - 2 offensive adjustment triggers (if your offense stalls)
  - 2 defensive adjustment triggers (if their offense is getting good looks)
  - 1 personnel adjustment trigger (if a specific matchup is being exploited)
  - 1 late-game trigger (if you are protecting a lead or trailing by 4-8 with under 4 minutes)

HALF-TIME ADJUSTMENT PRIORITIES
   If the first half goes as their scouting report suggests:
   What are the top 3 things to address at halftime?
   Order by priority. Be specific about what to tell the team.

PRACTICE PLAN — PRE-GAME PREPARATION

What should be covered in the practice sessions before this game?
Organize as a 3-day practice plan. Not every item needs to be an hour drill — some are 10-minute
emphasis reminders. A coach can pick what fits their schedule.

DAY 1 — OFFENSE (60-75 min total)
  List 3-5 specific practice items. For each:
  - Drill or activity name
  - What opponent tendency it prepares for
  - Time allocation (10 min, 15 min, etc.)
  Focus: installing the offensive game plan against their primary defense.

DAY 2 — DEFENSE (60-75 min total)
  List 3-5 specific practice items. For each:
  - Drill or activity name
  - What opponent tendency it prepares for
  - Time allocation
  Focus: defending their primary sets and ball screen actions.

DAY 3 — SCOUT AND SITUATIONAL (30-45 min total)
  Light day. Focus on:
  - Walk-through of their top 3 offensive sets (scout team runs them)
  - Walk-through of their ball screen coverage vs your actions
  - Late-game situational reps
  No hard work. Recognition and reinforcement only.

OUTPUT FORMAT:
Write under the exact headings and sub-headings above.
The adjustment triggers must be formatted exactly as shown — TRIGGER / If / Then / Tell your team.
The practice plan must have all three days with explicit time allocations.
Every item must tie back to something in the scouting report context.
A coach should be able to hand this section to an assistant coach and say "run this" without further clarification.
```

---

## PROMPT VERSIONING PROTOCOL

When Tommy updates a prompt:

1. Edit the `.txt` file in `backend/prompts/`
2. Increment the version: `v1.0` → `v1.1` → `v1.2` → etc. Major rewrites get `v2.0`.
3. Add a one-line changelog entry describing what changed and why.
4. Commit. The new version is live on the next report generated.
5. The film analysis cache for the old version is now stale — workers will miss on cache lookups
   for `film_hash + old_version` and re-run analysis. This is correct behavior.
6. Run the eval question for the affected section (from EVALS.md) on the next 3 reports generated
   with the new version before declaring the change an improvement.

**Version format rules:**
- `v1.0`: initial
- `v1.1`: minor addition (new instruction, clarified language, added output requirement)
- `v1.2`: behavior change (changed how something is counted, reordered sections, new format rule)
- `v2.0`: full rewrite of the prompt body

**Never edit a prompt without bumping the version.** An unbumped edit makes it impossible to
correlate corrections to the prompt that generated them. The version is the primary audit key.

---

### Composite cache key (`film_analysis_cache.prompt_version`)

The value written to `film_analysis_cache.prompt_version` (and used for lookup) is composed
from the prompt-file headers at runtime by `services/prompt_versions.py::get_film_analysis_cache_prompt_version()`.
Format:

```
{sections_prompt_version}|{preprocess_prompt_version}
```

- **`sections_prompt_version`** is the `VERSION:` header of `offensive_sets.txt`. This file
  is the **sentinel** for the entire 6-section bundle. If you bump any other section prompt
  (`defensive_schemes.txt`, `pnr_coverage.txt`, `player_pages.txt`, `game_plan.txt`,
  `adjustments_practice.txt`) **without** also bumping `offensive_sets.txt`, the cache key
  does **not** change and stale cached sections will be served. Convention: bump all six
  section prompts to the same version on every release that touches any of them. The
  sentinel is `offensive_sets.txt` only because it is the alphabetical first — there is no
  semantic significance.

- **`preprocess_prompt_version`** is normally the shared `VERSION:` of `chunk_extraction.txt`
  and `chunk_synthesis.txt` (today: `v1.6`). If the two files end up with different versions
  (e.g. you bump only one), the loader joins them with `+`:

  ```
  preprocess_v = f"{v0a}+{v0b}"   # e.g. "v1.7+v1.6"
  ```

  This forms a deliberately ugly key (`v1.0|v1.7+v1.6`) so that diverged-version states are
  obvious in logs and Neon. Aligned versions are the norm; the `+` join exists to keep the
  cache key correct during the brief window between bumping one preprocess prompt and the
  other.

Example composite keys:
- All-aligned today: `v1.0|v1.6`
- After bumping `offensive_sets.txt` to v1.1 (other sections aligned): `v1.1|v1.6`
- During a Prompt 0A bump but 0B not yet aligned: `v1.0|v1.7+v1.6`

A prompt edit that produces a new composite key invalidates every cached entry at the old
key — the next report run for that film re-executes all 4 sections (and re-executes Prompts
0A + 0B if the preprocess half of the key changed). This is the intended behavior.

---

## PROMPT QUALITY RULES

These rules apply to every prompt in this file and to any future prompt Tommy writes.

**Rule 1 — Ground every instruction in a specific output.**
Bad: "Be detailed."
Good: "Count occurrences. If you observed a set 11 times, write 11."
The model follows instructions that produce a specific observable output. Abstract quality instructions produce abstract output.

**Rule 2 — Name the failure mode you are preventing.**
Every negative instruction ("do not," "avoid") must reference a specific failure you have seen or anticipate.
Bad: "Do not be vague."
Good: "Do not round to the nearest 5 or fabricate precision you do not have."
The model cannot avoid a failure it cannot identify.

**Rule 3 — The output format section is not optional.**
Every prompt ends with an explicit OUTPUT FORMAT section. If the output format is not specified,
the model will invent one. The PDF template expects a specific structure. Invented structure breaks assembly.

**Rule 4 — Use example outputs for the most critical instructions.**
Wherever the difference between a useful answer and a useless answer is subtle, include an example.
"'#3 Williams initiates the Horns action from the top every time — his tell is a right-hand signal
to the bigs before the ball crosses half court' is useful. 'They run some sets' is not."
This pattern anchors the model to the correct specificity level better than any abstract instruction.

**Rule 5 — Coaching vocabulary is not optional.**
The output goes to coaches who will be annoyed by generic language. Use the vocabulary coaches use:
drop, hedge, ICE, blitz, DHO, pin-down, floppy, elbow, short corner, nail, dunker spot.
If you add a new prompt and are unsure of the vocabulary for a section, ask Tommy before writing it.

**Rule 6 — Every player referenced must come from the roster.**
Prompts for sections 1-4 instruct Gemini to attribute everything to jersey numbers and names from the roster.
Never allow a prompt to produce generic player references ("their point guard," "their center").
The roster is in the context cache. Gemini can and must use it.

---

## PROMPT → PDF SECTION MAPPING

```
Prompt file                  PDF section              PDF page order
───────────────────────────────────────────────────────────────────
offensive_sets.txt           Offensive Sets           2
defensive_schemes.txt        Defensive Schemes        3
pnr_coverage.txt             Pick and Roll Coverage   4
player_pages.txt             Individual Player Pages  5
game_plan.txt                Game Plan                6
adjustments_practice.txt     In-Game Adj + Practice   7
```

Cover page (page 1) is generated by the PDF template directly — no Gemini call, no prompt.
It contains: team name, report date, TEX branding.

---

*Last updated: 2026-05-19 — Prompt 0A/0B re-mirrored at v1.6 (D-023); composite cache key documented; loader snippet aligned with `services/prompts.py`.*
*Current prompt versions: sections 1–6 at v1.0, Prompts 0A/0B at v1.6.*
*Prompt changes require version increment + EVALS.md validation before declaring improvement.*
*Post-eval iteration of Prompts 0A/0B is tracked in GitHub Issue #28.*
