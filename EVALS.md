# EVALS.md — TEX v2

Evaluation framework. How we know TEX is working.
Every feature has an eval question. Every prompt has an eval rubric.
A task is not done until the eval passes. A prompt update is not an improvement until the
eval confirms it.

Read PRD.md for feature definitions. Read PROMPTS.md for prompt versions being evaluated.

This document defines **what** to evaluate and **how** to grade it. Read `TRAINING.md` §4
for the golden set (the films being graded) and `TRAINING.md` §4.5 for the internal
grading UI (the tool that grades them). Read `ROADMAP.md` → COMMERCIAL READINESS LADDER
Stage 1 for the commercial gate these evals must clear before TEX ships to any coach.

**Canonical prompt versions under evaluation: 0A v1.6, 0B v1.6 (see PROMPTS.md).**
Earlier prompt versions are historical, not active. Eval scorecards keyed to older
versions should be treated as reference, not as current pass/fail.

---

## TWO TYPES OF EVALS

**Infrastructure evals** — binary. Either it works or it doesn't. No partial credit.
A film either lands in R2 with the correct metadata, or it does not. The eval answer is
yes or no. These run once when the feature is built and again any time something changes
that could break it.

**Prompt evals** — scored. Two complementary scoring systems run alongside each other:

1. **Rubric scores** (1-5 per dimension) — the per-prompt rubrics later in this document.
   Useful for catching specific prompt failure modes (e.g., "vocabulary reconciliation
   broke" or "personnel attribution accuracy dropped").
2. **Golden-set outcome scores** (captured / missed / hallucinated per claim) — produced
   by the internal grading UI when Tommy clicks through a graded report against a
   golden-set ground-truth document. The methodology lives in `TRAINING.md` §4.5; the
   per-run results are written to `EVAL_SCORES.md` at the repo root.

A prompt update that improves rubric scores but **regresses golden-set captured%** is a
regression. Both signals must hold. The rubric catches structural issues; the golden-set
outcome catches whether the prompt actually produces correct claims about real game film.

---

## EVAL HARNESS — CURRENT STATE

What exists on disk today:

```
✓ golden_set/                                  5 ground-truth folders, one per film
  ├── film_01_bbe_vs_team_durant/              ground_truth.md, metadata.md, film_watch_notes.md
  ├── film_02_rebels_vs_az_unity/              (same structure)
  ├── film_03_spire_vs_la_lumiere/
  ├── film_04_montverde_vs_brewster/
  └── film_05_la_lumiere_vs_oak_hill/
✓ golden_set/README.md                         workflow + ground-truth doneness rubric

✓ Backend Prompt 0A/0B v1.6 prompts            backend/prompts/chunk_extraction.txt + chunk_synthesis.txt
✓ Backend section 1-6 v1.0 prompts             backend/prompts/{offensive_sets,defensive_schemes,pnr_coverage,player_pages,game_plan,adjustments_practice}.txt
✓ composite prompt_version derivation          backend/services/prompt_versions.py
```

What does **not** yet exist on disk:

```
✗ backend/evals/eval_log.csv                   referenced below as the rubric log; NOT YET CREATED
✗ EVAL_SCORES.md (repo root)                   referenced below as the golden-set log; NOT YET CREATED
✗ Internal grading UI                          described in TRAINING.md §4.5; NOT YET BUILT
✗ Automated eval runner / CI integration       no current script invokes the rubrics or golden-set comparison
```

The rubrics in this document are usable today as a human grading aid (Tommy reads the
output, scores against the rubric, writes the result somewhere). Automated harness work
is queued — until it lands, treat eval rows below that depend on the harness as **manual**.

---

## INFRASTRUCTURE EVALS

These match the eval questions in PRD.md. Collected here as a single runnable checklist.

```
FEATURE                          EVAL QUESTION                                            PASS CONDITION
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
Auth                             Can a coach sign up, log in, and see only their data?    users row in Neon, JWT valid, zero data from other accounts visible
Clerk webhook                    Does user.created write a users row?                     Row exists with correct clerk_id and email within 5 seconds of signup
Teams                            Can a coach create a team and see it on dashboard?       teams row in Neon with correct user_id, renders on /dashboard
Roster                           Can a coach add 10 players?                              10 rows in roster_players, scoped to correct team_id and user_id
Duplicate jersey                 Does adding a duplicate jersey number return 409?         409 returned, no duplicate row created
Film upload (browser → R2)       Does the file land in R2 at the correct key?             Object exists at films/{user_id}/{film_id}/{filename}, films row shows status=uploaded
Film validation L1 (browser)     Does a non-video file get rejected before upload?        Error shown in UI before any network request, R2 untouched
Film validation L2 (FastAPI)     Does the upload-initiate endpoint validate file?         ⚠️ NOT CURRENTLY IMPLEMENTED. POST /films/upload-initiate accepts any file_name/file_size — no MIME or extension check happens server-side before the presigned URL is issued. Layer 3 (FFprobe in worker) is the real gate today. Flagged as a future eval target.
Film validation L3 (FFprobe)     Does a corrupted video file fail at the worker?          films.status=error with validation message, /tmp cleaned, no Gemini calls made
Film under 1 minute              Does a 30-second clip get rejected?                      films.status=error, "Film is under 1 minute" (services/ffprobe.py:112)
Film over 3 hours                Does a 4-hour file get rejected?                         films.status=error, references 3-hour limit (services/ffprobe.py:118)
Film processing                  Do chunks land in Gemini with correct DB state?          film_chunks rows with non-null gemini_file_uri, gemini_file_state='active', expires_at populated
Prompt 0A (extract_chunk)        Does each chunk produce a structured extraction log?     film_chunks.extraction_output populated, extraction_status='complete' per chunk
Prompt 0B (run_chunk_synthesis)  Does synthesis produce the full-game intelligence doc?   film_analysis_cache row with non-null synthesis_document at the current composite prompt_version
Prompt 0B failure (D-025)        Does a 0B failure transition films to error?             films.status='error', error_message references synthesis. Sections 1-4 do NOT run. (no graceful degradation)
process_film timeout (D-026)     Does a stuck process_film hit the 120-min hard limit?    SoftTimeLimitExceeded at 7000s; films.status='error', message="Processing timed out after 120 minutes"
/tmp cleanup (success)           Is /tmp empty after a successful task?                   ls /tmp on worker shows no {film_id}_* files
/tmp cleanup (failure)           Is /tmp empty after a failed task?                       ls /tmp on worker shows no {film_id}_* files after intentional failure
URI expiry check                 Does an expired URI trigger re-upload from R2?           Developer-API backend: set gemini_file_expires_at to past, confirm re-upload runs, new URI saved. Vertex backend: no-op (GCS URIs do not expire).
Synthesis-only sentinel cache    Is the report-generation "cache" a sentinel, not Google? (D-024) cache_uri returned by create_context_cache starts with "vertex:no-cache:"; no Google CachedContent created; sections 1-4 sent text Parts only
Parallel sections                Do sections 1-4 fire as a single chord?                  In Celery logs: chord of 4 run_section tasks dispatched simultaneously; chord callback fires after all 4 terminal
Section-cache short-circuit      Does a regeneration of the same single-film report skip the chord? On second report on same film_id at same composite prompt_version: report_sections written with model_used='cached'; section_generation chord not invoked
Section fallback (Flash → Claude) Does Claude fire when Flash fails on sections 5-6?       With Flash endpoint blocked: section completes via Claude; report_sections.model_used='claude-3-5-sonnet'. ⚠️ fallback_events row NOT written today — see Issue #27.
Dead letter                      Does a task that exhausts retries write a row?           After 3 forced failures: dead_letter_tasks row with full args, film_id, user_id
PDF export                       Does the PDF contain cover + 6 sections?                 No blank pages; player_pages section has one block per rostered player; errored sections render placeholders
Payment — free first report      Does the first report skip Stripe?                       POST /reports returns {payment_required: false, report_id}; report generates
Payment — paid second report     Does the second report return a payment-required flag?   POST /reports returns {payment_required: true, team_id, film_ids}; frontend follows with POST /stripe/create-checkout-session; report row NOT created until checkout.session.completed webhook fires
Payment — credit                 Does a credit skip Stripe checkout?                      user.report_credits > 0: payment_required: false, report generates immediately, credits decremented by 1
Stripe webhook signature         Does the webhook reject an unsigned payload?             POST /stripe/webhook returns 400 when stripe-signature header missing or invalid. verify_webhook (services/stripe_client.py) raises before any DB write.
Clerk webhook signature          Does the Clerk webhook reject an unsigned payload?       POST /webhooks/clerk returns 400 when svix-signature header missing or invalid (routers/webhooks.py)
Failure credit                   Does a failed report apply a credit automatically?       report.status='error' → users.report_credits incremented by 1; notification of type='report_failed_credit_applied' written
Training mode admin gate         Can a non-admin access /admin/* routes?                  403 returned for every /admin route with a non-admin Clerk JWT. require_admin runs a live SELECT is_admin on every request.
Correction save                  Does a correction save with exact ai_claim text?         corrections row matches submitted text exactly, prompt_version matches the composite key from prompt_versions.py
Notification                     Does a coach see a notification when report is ready?    notifications row written with notification_type=report_complete (or report_partial / report_failed_credit_applied)
Startup recovery                 Does recover_stuck_jobs() re-enqueue stuck films?        Film with status='processing' and updated_at > 2 hours ago gets re-enqueued on worker boot
Rate-limit buckets               Do the three buckets enforce independently?              In Redis: separate keys for gemini-2.5-pro, gemini-2.5-flash, gemini-file-api; exceeding one's limit does not block the others
SDK HTTP timeout regression      Does _get_dev_client set http_options.timeout=300_000?   services/ai/gemini.py:_get_dev_client passes types.HttpOptions(timeout=300_000); regression-test by reading the file at CI time
Prompt-version cache invalidation Does a prompt-file bump invalidate film_analysis_cache reads? Bump VERSION: in chunk_extraction.txt (or offensive_sets.txt sentinel): next report on the same film_hash re-runs the corresponding stage. composite key from get_film_analysis_cache_prompt_version()
film_chunks cleanup after report Are R2 chunks deleted after reports.status terminal?     For each chunk: R2 object gone; gemini_file_state='deleted' in DB row. Cleanup runs in assemble_and_deliver only after reports.status is written.
Chord partial degradation        Does a chord with some errored sections still assemble?  1-5 sections errored: assemble_and_deliver writes PDF with placeholder pages; reports.status='partial'; no failure credit applied. All 6 errored: reports.status='error', failure credit applied.
Redis AOF                        Does Redis recover queued tasks after a restart?         Queue a task, restart Redis, confirm task is still in queue and executes
```

**How to run an infrastructure eval:**
Each eval has a specific action that produces a verifiable state in Neon, R2, Redis, or
logs. Run the action, query the expected state, compare. If the state matches, the eval
passes. Do not mark a feature done based on "it seemed to work." Query the database or
check the bucket.

**Observability-eval gap:** Several evals above could be replaced with Datadog alerts
once observability is wired (Issue #29). Until then, the checklist above is the
substitute — verified manually or by inspection.

---

## PROMPT EVALS

### EVAL PHILOSOPHY

Prompt quality cannot be evaluated by reading the output and deciding it "seems good."
That is not an eval. That is an impression. Impressions are wrong at scale.

Every prompt eval has a rubric with 5 dimensions scored 1-5. **In addition**, the
golden-set captured / missed / hallucinated outcome scores grade the prompt against a
hand-built ground-truth document. Both signals must hold.

**Rubric scoring scale:**

```
5 — Exceptional. A senior scout could use this output without edits.
4 — Good. Minor cleanup needed but the substance is correct and complete.
3 — Acceptable. Significant cleanup needed but the foundation is there.
2 — Poor. Major errors or omissions. Would mislead a coaching staff.
1 — Failing. Output is wrong, fabricated, or structurally broken.
```

**Golden-set outcome scoring (per TRAINING.md §4.5):**

```
captured %      = (claims in TEX output that match ground truth) / (claims in ground truth)
missed %        = 1 - captured%
hallucinated %  = (claims in TEX output NOT supported by ground truth) / (claims in TEX output)
```

A high captured% with high hallucinated% is a different failure mode than low captured%
with low hallucinated% — the first is over-confidence, the second is under-detection.
Both surface as actionable signals for the prompt author.

**Eval cadence:**

- On first deploy of a prompt: run against 3 reports, score all 3, take the average for
  the rubric; grade each report against its golden-set film if available, log to
  `EVAL_SCORES.md`.
- After any prompt update: run against the next 3 reports, compare to prior version
  averages on both rubric and golden-set outcome.
- Weekly: review correction data from the SCHEMA.md pattern analyzer for the current
  prompt version. High error rates in a category signal a dimension that needs a prompt fix.

---

### PROMPT 0A — CHUNK EXTRACTION EVAL (v1.6)

**File:** `backend/prompts/chunk_extraction.txt` (canonical v1.6)
**Eval question:** Does the extraction log from a single chunk contain accurate,
structured observation data that the synthesis prompt can reliably aggregate?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Count accuracy** | Occurrence counts match Tommy's manual recount within ±1 | Counts off by 2-3 | Counts fabricated or wildly wrong |
| **Attribution accuracy** | All actions attributed to correct jersey numbers (scouted-team roster names character-for-character) | 1-2 wrong jersey numbers or roster-name spellings | Multiple wrong attributions or jersey numbers not used |
| **Vocabulary consistency** | Canonical TEX labels used correctly (5-out, 1-4 flat, Horns, etc. per v1.6) | Mix of canonical and invented terms | Invented terminology that will block synthesis reconciliation |
| **Uncertainty flagging** | All genuine uncertainties surfaced in FLAGGED section | Some uncertainties surfaced | No flags despite observable ambiguities in the film |
| **Structural compliance** | All required sections present with correct headers | 1-2 sections missing or malformed | Output does not follow the required format |

**Pass threshold (rubric):** Average ≥ 3.5 across all 5 dimensions on 3 consecutive chunks.

**Most common failure modes to watch for (v1.6 specifics):**
- Burying high pick-and-roll possessions under "5-out motion" — explicitly forbidden in
  v1.6 (anti-bucketing rule). If you see this in output, the prompt's anti-bucketing
  block needs sharpening, not the model.
- Inventing opponent player full names — v1.6 says opponent identities are `#[N]` only,
  with optional `(announcer said "...")` for heard-only tags. Invented names = a hard
  fail on Attribution accuracy.
- Defended PnR `[CONFIRMED]` tags with thin sample — v1.6 caps confidence at `[LIKELY]`
  when N < 4.

---

### PROMPT 0B — CHUNK SYNTHESIS EVAL (v1.6)

**File:** `backend/prompts/chunk_synthesis.txt` (canonical v1.6)
**Eval question:** Does the synthesis document accurately represent the full game with
reconciled counts, unified vocabulary, correctly tagged confidence levels, and explicit
arithmetic for every aggregated count?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Aggregation accuracy** | Every count is shown as explicit segment arithmetic (`chunk0:X + chunk1:Y + … = Total`) and the total matches the sum | Counts shown without segment arithmetic or off by 1-2 | Counts do not match extractions — synthesis invented numbers |
| **Vocabulary reconciliation** | All reconciliation decisions documented; Horns kept separate from 5-out per v1.6 | Some reconciliations undocumented; one ambiguous merge | No reconciliation — duplicate entries for the same action, or Horns folded into 5-out |
| **Timeline preservation** | Scheme/coverage changes documented with game context | Changes noted without timing | Timeline collapsed — "they played a mix" type flattening |
| **Contradiction handling** | Every contradiction surfaced and resolved with confidence level | Some contradictions resolved silently | Contradictions silently resolved or ignored |
| **Confidence + final-score discipline** | [CONFIRMED]/[LIKELY]/[SINGLE GAME SIGNAL] tags accurate; final score follows v1.6 evidence ladder OR explicit "insufficient observation" | Tags present but miscalibrated; final score weakly justified | No confidence tags; final score guessed from a flaky ticker |

**Pass threshold (rubric):** Average ≥ 4.0 across all 5 dimensions. Higher bar than
extraction because synthesis errors propagate into all 6 report sections.

**How to verify aggregation accuracy:**
Sum the counts from all chunk extraction outputs manually for the top 3 actions. Compare
to synthesis totals. They must match exactly per Rule 1 in the synthesis prompt. v1.6
requires the synthesis to **show its work** — if a section doesn't include the
`chunk0:X + chunk1:Y + …` line, that's a rubric fail on Aggregation accuracy regardless
of whether the total happens to be right.

**How to verify timeline preservation:**
Watch the last 5 minutes of the film. Identify any scheme change. Confirm the synthesis
document documents it. If a visible scheme change is absent, timeline preservation is failing.

---

### SECTION 1 — OFFENSIVE SETS EVAL

**File:** `backend/prompts/offensive_sets.txt`
**Eval question:** Does a coach reading the Offensive Sets section have an accurate,
complete picture of what this opponent runs offensively — with counts, personnel, and
game plan implications?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Set identification accuracy** | All primary sets correctly named using coaching vocabulary | 1-2 sets misidentified | Primary set wrong |
| **Count accuracy** | Occurrence counts match Tommy's recount within ±1 | Off by 2-3 | Fabricated or no counts provided |
| **Personnel attribution** | Every action attributed to correct jersey numbers from roster | 1-2 misattributions | Jersey numbers absent or wrong |
| **Counter and variation coverage** | Counters off primary actions documented | Counters mentioned but vague | No counters documented |
| **Output usability** | Section reads like a scout's report | Readable but missing specificity | Generic, could apply to any team |

**Pass threshold:** Average ≥ 3.5. Count accuracy and set identification below 3
individually triggers a prompt fix regardless of overall average.

**Tommy's manual check:**
Watch 10 consecutive half-court possessions. Count every occurrence of the primary set
TEX identifies. If Tommy's count differs from TEX's count by more than 2, count accuracy
is failing.

---

### SECTION 2 — DEFENSIVE SCHEMES EVAL

**File:** `backend/prompts/defensive_schemes.txt`
**Eval question:** Does a coach reading the Defensive Schemes section know exactly what
defense they will face, where the gaps are, and which players are the liabilities?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Scheme identification** | Base defense correctly identified with percentage breakdown | Correctly identified but no percentages | Wrong base defense identified |
| **Scheme change documentation** | All defensive adjustments documented with triggers | Adjustments noted but triggers missing | No scheme changes documented despite visible ones |
| **Liability identification** | Weakest defender identified by jersey number with specific vulnerability | Weak defenders noted without specific vulnerability | No defensive liabilities identified |
| **Help principle accuracy** | Help rotation principles described accurately and specifically | Described but vague | Absent or wrong |
| **Actionability** | A coach can draw up 2-3 specific actions to attack this defense after reading | Some attack options implied | No actionable intel |

**Pass threshold:** Average ≥ 3.5. Scheme identification below 3 triggers immediate prompt fix.

---

### SECTION 3 — PICK AND ROLL COVERAGE EVAL

**File:** `backend/prompts/pnr_coverage.txt`
**Eval question:** Does a coach reading the PnR section know exactly what coverage they
will face in ball screen actions and exactly how to attack it?

This is the highest-stakes section in the report. PnR actions represent 30-50% of
possessions at every level above high school. A wrong coverage identification sends a
coaching staff into a game with a fundamentally broken game plan.

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Coverage identification** | Primary coverage correctly named (drop/hedge/switch/ICE/blitz) | Correct primary but wrong secondary | Wrong primary coverage |
| **Personnel-based variation** | Coverage changes by matchup documented with jersey numbers | Variations noted without personnel specificity | No variations documented despite visible ones |
| **Execution quality assessment** | Specific breakdown point identified with evidence | Breakdown noted without specificity | "They execute well" — no specificity |
| **Offensive PnR tendencies** | Ball handler reads, screener pop/roll preference documented with counts | Present but incomplete | Absent |
| **Defensive and offensive coverage present** | Both Part A and Part B complete | One part significantly shorter than the other | Only one part present |

**Pass threshold:** Average ≥ 4.0. Coverage identification below 3 is a critical failure
— triggers immediate prompt fix and manual review of any reports generated with that
prompt version.

**Tommy's manual check:**
Watch 10 ball screen possessions. Identify the coverage on each. The modal coverage is
the "primary coverage." If TEX identifies a different primary coverage, this is a
critical failure.

---

### SECTION 4 — INDIVIDUAL PLAYER PAGES EVAL

**File:** `backend/prompts/player_pages.txt`
**Eval question:** Does each player profile give a coaching staff an accurate, actionable
picture of that player?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Completeness** | Every rostered player has a profile | 1-2 players missing | Multiple players missing |
| **Offensive profile accuracy** | Scoring zones, dominant hand, primary actions correct | 1-2 errors | Primary action wrong |
| **Defensive liability specificity** | Explicit vulnerability with evidence | Liability noted without evidence | "Below-average defender" — no specific vulnerability |
| **Scouting note quality** | The note changes how the staff prepares — specific, actionable, tied to the film | Generic positive or negative assessment | Absent or content-free |
| **Jersey number accuracy** | All profiles correctly attributed to the right player | 1 misattribution | Multiple misattributions |

**Pass threshold:** Average ≥ 3.5. Jersey number accuracy below 4 triggers immediate fix
— a misattributed profile actively misleads the coaching staff.

---

### SECTION 5 — GAME PLAN EVAL

**File:** `backend/prompts/game_plan.txt`
**Eval question:** Does a head coach reading the Game Plan section have a specific,
film-grounded offensive and defensive approach ready to install?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Grounding in scouting report** | Every recommendation cites specific evidence from sections 1-4 | Most recommendations cited | Recommendations that could apply to any team |
| **Offensive specificity** | Top-3 actions named with specific reasoning for this defense | Actions named but reasoning generic | "Run your best plays" type content |
| **Attack-the-liability clarity** | Specific player targets identified with the exact action to run at them | Targets identified without specific action | No player-specific attack plan |
| **Defensive recommendation quality** | Coverage recommendation with specific reasoning tied to their PnR personnel | Coverage recommended without reasoning | Generic defensive advice |
| **Avoid list accuracy** | "Actions to avoid" match what this defense actually takes away | Partially accurate | Absent or wrong |

**Pass threshold:** Average ≥ 3.5. Grounding score below 3 is a critical failure.

---

### SECTION 6 — IN-GAME ADJUSTMENTS + PRACTICE PLAN EVAL

**File:** `backend/prompts/adjustments_practice.txt`
**Eval question:** Can a coaching staff hand the Adjustments section to an assistant
coach and say "run this" without further clarification?

**Rubric:**

| Dimension | Score 5 | Score 3 | Score 1 |
|---|---|---|---|
| **Trigger specificity** | TRIGGER/If/Then format followed, conditions are observable in-game | Format followed but conditions are vague | Format not followed or conditions are not observable |
| **Adjustment actionability** | "Tell your team" instruction is usable in a 60-second timeout | Actionable but too long for a timeout | Abstract |
| **Practice plan specificity** | Each drill tied to a specific opponent tendency with time allocation | Drills listed without opponent tie | Generic drills |
| **Coverage of failure modes** | Offensive, defensive, personnel, and late-game triggers all present | 3 of 4 covered | 1-2 covered |
| **Halftime priorities quality** | 3 specific priorities a staff could implement in 10 min | Present but generic | Absent or too many (more than 3) |

**Pass threshold:** Average ≥ 3.5.

---

## FULL-PIPELINE EVAL

Run this after every complete system change (new prompt version, infrastructure change,
Gemini model update). This is the end-to-end test.

**Test input:** A real game film that Tommy has personally scouted — ideally one of the
5 golden-set films so the ground-truth document is already built.
**Test output:** A complete TEX scouting report PDF.
**Evaluator:** Tommy.

**Questions Tommy answers after reading the full report:**

```
1.  Did TEX correctly identify the opponent's primary offensive set?                   Y / N
2.  Did TEX correctly identify the opponent's base defensive scheme?                   Y / N
3.  Did TEX correctly identify the primary ball screen coverage?                       Y / N
4.  Are the occurrence counts within ±2 of your manual counts for the top 3 actions?   Y / N
5.  Did TEX correctly identify the weakest defensive player?                           Y / N
6.  Would you use this game plan as a starting point for your actual game prep?        Y / N
7.  Did any section contain information that would actively mislead your staff?        Y / N
8.  How many claims did you need to correct in training mode after reading?            [count]
9.  How long did it take to read the full report and feel prepared?                    [minutes]
10. Would you pay $49 for this report?                                                 Y / N
```

**Pass conditions:**
- Questions 1-5: at least 4 of 5 yes
- Question 6: yes
- Question 7: no (any yes here is a P0 issue regardless of other scores)
- Question 8: fewer than 10 corrections needed
- Question 9: under 20 minutes to feel prepared
- Question 10: yes

If the full-pipeline eval does not pass, the system is not ready for real coaches
regardless of what individual prompt evals show. Unit tests passing does not mean the
product works.

---

## EVAL TRACKING

Two files **will** act as the single source of truth for eval state once the harness lands:

- **`backend/evals/eval_log.csv`** — prompt-dimension rubric scores. One row per prompt
  version evaluation. **Does not exist on disk yet.**
- **`EVAL_SCORES.md`** — golden-set outcome scores (captured / missed / hallucinated)
  written by the internal grading UI on every graded run. **Does not exist on disk yet.**

The two files capture different signals. The CSV answers "did this prompt version hit
its rubric?" The Markdown file answers "how did TEX do against hand-graded ground truth
on the golden set?" Both must improve over time. A prompt version that improves rubric
scores but regresses golden-set captured% is a regression.

**Planned format of `backend/evals/eval_log.csv`:**

```
DATE        PROMPT          VERSION   REPORTS_EVALUATED   DIM1  DIM2  DIM3  DIM4  DIM5  AVG   PASS  NOTES
2026-04-01  offensive_sets  v1.0      3                   3.7   4.0   3.3   3.0   4.0   3.6   Y     baseline
2026-04-08  offensive_sets  v1.1      3                   4.0   4.0   3.7   3.3   4.3   3.9   Y     +0.3 improvement
2026-04-08  pnr_coverage    v1.0      3                   2.7   3.3   3.0   3.7   4.0   3.3   N     coverage_id failing
```

**Planned format of `EVAL_SCORES.md`:** auto-written by the internal grading UI
(TRAINING.md §4.5). One row per film per graded run, columns: date, `prompt_version`,
film_id, captured %, missed %, hallucinated %, total claims, freeform notes. Tommy does
not edit it by hand — the grading UI writes it as a side effect of clicking through a
graded report.

Until the grading UI is built, log eval runs informally in `tmp_*.txt` snapshot files
under repo root (the same pattern already used for Prompt 0B golden-set checks).

---

## WHAT MAKES AN EVAL QUESTION GOOD

An eval question is good if:
1. It has a binary or numeric answer — not "did it seem good?"
2. The answer can be verified without asking the model to evaluate itself.
3. A failing answer points to a specific fix.

An eval question is bad if:
1. It is answered by reading the output and deciding it is "high quality."
2. It can be passed by a hallucinated but plausible-sounding output.
3. Passing it does not mean the feature actually works for a coach.

The eval question "Does the report look professional?" is bad. It fails all three criteria.
The eval question "Does the primary ball screen coverage match what Tommy observes in 10
manual possessions?" is good. It is verifiable, human-grounded, and failure points to a
specific prompt fix.

---

*Last updated: 2026-05-19 — Aligned to synthesis-only mode (D-024). L2 film validation*
*eval flagged as not-currently-implemented (worker FFprobe is the real gate). Section*
*fallback eval notes fallback_events writes deferred (Issue #27). New evals added:*
*synthesis-only sentinel cache, section-cache short-circuit, prompt-version cache*
*invalidation, rate-limit buckets, SDK HTTP timeout regression, Stripe + Clerk webhook*
*signature verification, chord partial degradation, film_chunks cleanup after report.*
*Golden-set captured/missed/hallucinated methodology surfaced alongside rubrics.*
*backend/evals/eval_log.csv and EVAL_SCORES.md flagged as not-yet-created. Canonical*
*0A v1.6 / 0B v1.6 prompt-version anchor added.*
*Eval framework version: v1.1*
