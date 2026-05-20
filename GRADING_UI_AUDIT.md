# GRADING_UI_AUDIT.md

## Decisions locked 2026-05-19

These decisions are final for the v1 grading UI build. Do not 
re-litigate during implementation.

- **Build approach:** Option 1 — build the real grading UI properly 
  (not v0 shortcut), sized to ~27-38 hours / 4 focused days.
- **R6 schema:** Option A — add `claim_status text` column to 
  corrections table (values: `'captured'` | `'missed'` | `'hallucinated'`). 
  Make `ai_claim` nullable so Missed rows store ground-truth text 
  only. Drop or recompute the `is_correct NOT NULL` constraint.
- **R9 claim walker:** v1 sentence-split (client-side sentence 
  segmentation, 4h estimate). Structured-claims upgrade is post-MVP.

---

**Coverage: ~38% — 5 of 13 requirements fully built, 2 partial, 6 missing.**
TRAINING.md §4.5 estimates the existing `/admin` is ~60% of what's needed. That number is **optimistic**. The corrections *infrastructure* (table, write endpoint, admin gate, list/pattern dashboards) is real and reusable. But the actual graded-evaluation *workflow* — load ground truth, walk a report claim-by-claim, three-way classify in one click, auto-emit EVAL_SCORES + snapshot — is **greenfield**. The current "New Correction" form is a manual single-row entry that requires Tommy to copy/paste `report_id`, `film_id`, the `ai_claim` text, section, category, and prompt version per claim. That is the slow path; the grading UI replaces it.

Audited on branch `feature/grading-ui` (just created from `feature/doc-refresh-costs-stack-flows-evals`).

---

## Requirements extracted from TRAINING.md §4.5

The spec (TRAINING.md:122-163) plus the explicit checklist in the user's audit brief breaks into 13 atomic requirements. I split "what gets written on save" into three rows (corrections DB / EVAL_SCORES.md / disk snapshot) because each has independent build cost.

| # | Requirement | Status | Files / lines | Notes |
|---|---|---|---|---|
| R1 | Admin gate (`is_admin` checked on every request, not just login) | ✅ BUILT | `backend/routers/admin.py:50` (`Depends(require_admin)` on every route); `frontend/app/admin/layout.tsx:21-28` | Every admin route is gated by `require_admin`. Frontend layout probes `/admin/users` to decide whether to render — acceptable. |
| R2 | Corrections table matches production coach-corrections schema | ✅ BUILT | `backend/migrations/009_create_corrections.sql`; `SCHEMA.md:398-453` | Schema 1:1 with AI_STRATEGY.md §Phase-4 spec (`AI_STRATEGY.md:477-498`). `phase` default 1, `game_count` nullable, `is_correct` boolean. Same table for production + training, per AI_STRATEGY.md. |
| R3 | Write path: one row per claim into corrections DB | 🟡 PARTIAL | `backend/routers/admin.py:144-206` (`POST /admin/corrections`); `frontend/lib/api.ts:351-371`; `frontend/app/admin/page.tsx:77-107` | Endpoint works and writes correctly. Three real gaps for grading-UI use: **(a)** manual entry — caller must pass `report_id`, `film_id`, `ai_claim`, `section_type`, `category`, `prompt_version` per row; no bulk endpoint, no auto-population from a selected report; **(b)** API model omits `phase` and `game_count` columns (silently defaulted on insert); **(c)** schema's `ai_claim text NOT NULL` cannot represent a "Missed" claim — the AI didn't produce text, so there is no `ai_claim`. See R6 — this is the load-bearing schema decision for the whole UI. |
| R4 | List existing corrections (filterable) | ✅ BUILT (bonus, not in §4.5) | `backend/routers/admin.py:49-117`; `frontend/app/admin/page.tsx:292-329` | Useful for review pass on prior grades. |
| R5 | Pattern analysis dashboard | ✅ BUILT (bonus, not in §4.5) | `backend/routers/admin.py:214-301`; `frontend/app/admin/patterns/page.tsx` | Built for the weekly analyzer in AI_STRATEGY.md. Bonus for grading — Tommy can see error rate per prompt_version after each grading session. |
| R6 | Captured / Missed / Hallucinated buttons (one-click, 3-way) | ❌ MISSING | n/a | Current form is binary `is_correct: true \| false`. Three-way classify needs **either** a new column (`claim_status text` with `'captured' \| 'missed' \| 'hallucinated'`) **or** a mapping convention (`captured = is_correct true`; `hallucinated = is_correct false`; `missed = ???`). The "Missed" case is the schema collision: `ai_claim NOT NULL` blocks any row that represents a claim TEX failed to make. **Decision needed before build starts** — see "What needs to be built" §6 below. |
| R7 | Side-by-side view (generated report + ground-truth doc) | ❌ MISSING | n/a | Current admin pages are single-column. Needs new route (e.g. `/admin/grade/[report_id]`) with a two-pane layout. No existing component to reuse. |
| R8 | Load golden-film ground-truth document alongside report | ❌ MISSING | n/a | `golden_set/film_04_montverde_vs_brewster/ground_truth.md` exists on disk; no backend endpoint to read it. No frontend selector to pick which ground-truth doc to pair with a report. Markdown is large (Film 04's `ground_truth.md` is the structured answer key) — needs either render-as-markdown or claim-segmented parsing. |
| R9 | Claim-by-claim walking interface | ❌ MISSING | n/a | Needs (1) a way to enumerate claims in the generated report — `report_sections.content` is free text, so this is either sentence-split, paragraph-split, prompt-restructured into bullets, or a manual click-to-anchor model. (2) State machine for "claim N of M". (3) Keyboard nav for speed. **This is the unknown-effort piece** — see effort table. |
| R10 | Optional correction text field per claim | 🟡 PARTIAL | `frontend/app/admin/page.tsx:225-236` | A `correct_claim` textarea exists in the single-correction form. It is only shown when `is_correct = false`. Logic and wire-up to the API exist; needs to be re-embedded in the per-claim walking UI and made truly optional (current API enforces "required when is_correct = false" at `admin.py:156-159`). |
| R11 | Auto-write scored summary line to `EVAL_SCORES.md` | ❌ MISSING | n/a | `EVAL_SCORES.md` does not exist in repo. No endpoint writes to it. Format per §4.5: `date \| prompt_version \| captured % \| missed % \| hallucinated % \| total claims \| notes`. Per AI_STRATEGY.md:83 this file *is* the eval-loop's primary score ledger. |
| R12 | Timestamped snapshot of full graded report to disk | ❌ MISSING | n/a | No snapshots directory, no writer. Likely shape: `eval_snapshots/{film_id}_{prompt_version}_{timestamp}.json` containing the report text, ground-truth ref, and every per-claim verdict. |
| R13 | Backend exposes AI-generated section *content* to the grader | ❌ MISSING | `backend/routers/reports.py:181-243` | `GET /reports/{id}` returns `SectionStatus` (status, model_used, generation_time) but **not** `report_sections.content`. The DB has it (`migrations/008_create_report_sections.sql:6`, column `content text`); the API just doesn't expose it. Grading UI can't function without an admin endpoint that returns full section text per report. |

**Coverage math:** 5 built + 2 partial + 6 missing = 13 requirements. Strict "fully built" rate = 5/13 = **38%**. If you count the two partials as half-credit, you get 6/13 = **46%**. Even the generous reading is well below the §4.5 estimate of 60%.

Where the 60% figure came from: counting infrastructure (admin gate + corrections table + write endpoint + listing + pattern dashboard) as a percentage of total LOC needed. That math holds for code volume but understates the *flow* gap — the actual side-by-side grading workflow is essentially greenfield.

---

## What needs to be built (in priority order)

Priority is "do this first because everything else depends on it" — not "easiest first."

### 1. **R6 schema decision: how to represent a "Missed" claim** (BLOCKING — 1h decision, 1-2h migration)
Cannot proceed without this. Two viable paths, both compatible with §4.5 + AI_STRATEGY.md:

- **Option A — add `claim_status text` column** to `corrections` with `'captured' \| 'missed' \| 'hallucinated'`. Drop the `is_correct` NOT NULL or compute it from `claim_status`. Make `ai_claim` nullable so Missed rows can store the ground-truth text in `correct_claim` only. This is the cleaner long-term schema; matches the 3-way mental model in §4.5 and surfaces in pattern analysis ("hallucination rate by section"). Migration is one new column + one nullable relax + a backfill (existing `is_correct=true` → `captured`, `is_correct=false` → `hallucinated`, no Missed rows yet).
- **Option B — keep schema, encode "Missed" as `ai_claim = ''` + `is_correct = false`**. Zero migration risk but loses analytical power and is brittle (empty-string sentinel). Not recommended.

**Recommendation: Option A.** Tommy should pick before the build starts tomorrow.

### 2. **R13 — Admin endpoint to fetch full report content** (3h)
New `GET /admin/reports/{report_id}` that returns `report_sections.content` for all 6 sections plus report metadata (film_id, prompt_version per section). Required by every other piece of the UI. Straightforward — read-only, admin-gated, joins `reports` + `report_sections`.

### 3. **R8 — Ground-truth loader** (3-5h)
- Backend: `GET /admin/golden-set/{film_slug}/ground-truth` reads `golden_set/{film_slug}/ground_truth.md` from disk. Admin-gated. Returns raw markdown.
- Backend: `GET /admin/golden-set` lists available golden films from filesystem.
- Frontend: dropdown selector on the grading page.
- Filesystem read inside FastAPI is fine for v1 (5 films, local files); productionize later if needed.

### 4. **R7 — Side-by-side layout** (4-6h)
New route `/admin/grade/[report_id]` with a two-pane layout (markdown-render the ground truth, render the report sections). Tailwind grid. Reuse `/admin` layout shell for the admin nav.

### 5. **R9 — Claim-by-claim walking interface** (6-10h, **most uncertain**)
Decide claim-extraction strategy first — this drives the build cost:

- **Cheapest (4h):** sentence-split the generated section content client-side. Tommy walks one sentence at a time. Works immediately. Noisy on long sentences containing multiple claims.
- **Better (8h):** add a `claims jsonb` column to `report_sections` populated by the section-generation prompts (ask Gemini to emit structured `claims: [...]` alongside prose). Requires prompt changes + migration but gives clean atomic claims.
- **Manual (6h):** Tommy click-drags to select claim text from the rendered report; selection becomes the `ai_claim`. Most flexible, slower per claim than auto-extraction but more accurate.

**Recommendation for v1: sentence-split now (4h), upgrade to structured claims after first 1-2 films graded.** Ship the loop before optimizing it.

Also needed: keyboard shortcuts (C / M / H + Enter), claim counter, jump-back navigation.

### 6. **R3+R10 — Wire per-claim save into the walking UI** (3-4h)
- Extend `POST /admin/corrections` (or add `POST /admin/corrections/batch`) to accept `claim_status` and the new nullable `ai_claim`.
- Auto-populate `report_id`, `film_id`, `section_type`, `prompt_version` from grading context — Tommy never types these.
- Per-claim correction textarea stays optional in UI; relax the "required when incorrect" check at `admin.py:156-159`.

### 7. **R11 — EVAL_SCORES.md auto-writer** (2-3h)
- Backend: `POST /admin/grading-sessions` accepts session metadata (film_id, prompt_version, totals, notes) and appends one row to `EVAL_SCORES.md` in the repo root.
- Decide on format. Suggested: a markdown table that grows by row, plus a JSON sidecar (`EVAL_SCORES.jsonl`) for machine-readable trend analysis. Both written in the same call.
- Initial file creation with a header on first session.

### 8. **R12 — Disk snapshot of graded report** (2h)
Same endpoint as R7 writes `eval_snapshots/{film_id}_{prompt_version}_{ISO8601}.json` with the report content, ground-truth doc reference, every per-claim verdict + correction. Plain `open(..., 'w')` — no R2 needed for internal eval data.

### 9. **Integration + testing pass** (4-6h)
- End-to-end: pick a generated report → load ground truth → walk through 50+ claims → submit → verify (a) N rows in corrections DB, (b) one new row in EVAL_SCORES.md, (c) one snapshot file. Repeat. Stopwatch the session — target ≤40 min for a full golden film. If not hit, identify the bottleneck and trim.
- Confirm same-table writes pass cleanly alongside any production-coach corrections (none exist yet, so safe).
- Sentry-instrument the per-claim save.

---

## Effort summary

| Item | Hours |
|---|---|
| R6 schema decision + migration | 2-3 |
| R13 admin report-content endpoint | 3 |
| R8 ground-truth loader (backend + frontend) | 3-5 |
| R7 side-by-side layout | 4-6 |
| R9 claim-by-claim walker (sentence-split v1) | 4-6 |
| R3+R10 per-claim save wiring | 3-4 |
| R11 EVAL_SCORES.md writer | 2-3 |
| R12 disk snapshot writer | 2 |
| Integration + manual test pass | 4-6 |
| **Total** | **27-38 hours** |

**Realistic calendar:** 4-5 focused dev days for a single builder. TRAINING.md §4.5's "2-3 days" estimate holds *only* if R9 stays at sentence-split v1 (no prompt-structured claims) and R6 picks Option A without iteration. If structured claims are pursued in v1, add 4-6h. If Option B is chosen and rejected after first use, add 2-3h to revert.

**What this audit deliberately excludes:** structured-claims prompt redesign, RLHF-style preference grading, multi-grader workflows, blind set support. Those are post-MVP and not in §4.5.

---

## Cross-references

- TRAINING.md §4.5 (lines 122-163) — the spec being audited
- AI_STRATEGY.md:83 — confirms grading UI is what makes the prompt-update loop run
- AI_STRATEGY.md:477-498 — production corrections schema (training + production share the same table)
- SCHEMA.md:398-453 — current `corrections` table
- ROADMAP.md → Commercial Readiness Ladder Stage 1 — engineering counterpart to §4.5
- `backend/routers/admin.py` — current admin surface (3 endpoints — corrections list/create, pattern analysis, users + credits)
- `frontend/app/admin/` — 3 pages: corrections, patterns, users
- `golden_set/film_01..05/ground_truth.md` — the 5 ground-truth docs already on disk

**No code was modified.** Audit only.
