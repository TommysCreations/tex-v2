# Grading UI Build Prompt — Day 1 Through Day 4

Paste this entire prompt into Claude Code on the morning of May 20 to 
begin the grading UI build. The build prompt assumes the prep work 
(checklist, decisions block, branch) is already in place.

---

Build the TEX v2 internal grading UI per TRAINING.md §4.5. The audit 
(GRADING_UI_AUDIT.md) identified ~38% existing coverage and 9 numbered 
build items. We're building all 9 properly, not a v0 shortcut.

## DECISIONS MADE (do not re-litigate)

- **R6 schema:** Option A — add `claim_status text` column to corrections 
  table (values: `'captured'` | `'missed'` | `'hallucinated'`). Make 
  `ai_claim` nullable so Missed rows can store ground-truth text only. 
  Drop or recompute the `is_correct NOT NULL` constraint.
- **R9 claim walker:** v1 sentence-split. Client-side sentence 
  segmentation of the rendered report. One sentence = one claim for 
  grading purposes. Structured-claims upgrade is post-MVP, not in scope 
  here.
- All other implementation choices per GRADING_UI_AUDIT.md recommendations.

## BUILD ORDER (do these in sequence, in this order)

### DAY 1 (Wed May 20)

**1. R6 schema decision + migration (1-2h)**
- Write Alembic migration adding `claim_status` column
- Update `ai_claim` to nullable
- Update SQLAlchemy model
- Run migration on dev branch
- Verify with SELECT against `corrections` table

**2. R13: Admin endpoint to fetch full report content (3h)**
- New route: `GET /admin/reports/{report_id}`
- Returns: all 6 sections' content + report metadata 
  (film_id, prompt_version per section)
- Admin-gated. Read-only. Joins `reports` and `report_sections`.

**3. R8: Ground-truth loader (3-5h)**
- Backend: `GET /admin/golden-set` — lists available golden films 
  from filesystem (read `golden_set/film_*/` directories)
- Backend: `GET /admin/golden-set/{film_slug}/ground-truth` — reads 
  `golden_set/{film_slug}/ground_truth.md` from disk, returns raw 
  markdown
- Frontend: dropdown selector on the grading page

### DAY 2 (Thu May 21)

**4. R7: Side-by-side layout (4-6h)**
- New route: `/admin/grade/[report_id]`
- Two-pane layout:
  - Left pane: rendered report sections (markdown-rendered)
  - Right pane: ground-truth document (markdown-rendered)
- Tailwind grid. Reuse `/admin` layout shell for admin nav.
- Sticky panes — both should scroll independently.

**5. R9: Sentence-split claim walker, v1 (4h)**
- Client-side: split each section's rendered content into sentences 
  (use a simple regex split on `.!?` or a small NLP library if needed)
- Each sentence rendered as a clickable element with three buttons 
  beside it: [Captured] [Missed] [Hallucinated]
- Optional textarea per claim for correction text
- Keyboard shortcuts: C (captured), M (missed), H (hallucinated), 
  Enter (next)
- Claim counter visible (e.g., "12 of 47 graded")
- Jump-back navigation (arrow keys or Prev/Next buttons)

**6. R3 + R10: Per-claim save wiring (3-4h)**
- Extend `POST /admin/corrections` (or add `POST /admin/corrections/batch`) 
  to accept `claim_status` and the new nullable `ai_claim`
- Auto-populate `report_id`, `film_id`, `section_type`, `prompt_version` 
  from grading context (no manual entry)
- Per-claim correction text optional in UI; relax the 
  "required when incorrect" check at admin.py:156-159
- Save on click (don't batch) so grading state survives reload

### DAY 3 EVENING (Fri May 22)

**7. R11: EVAL_SCORES.md auto-writer (2-3h)**
- Backend: `POST /admin/grading-sessions` accepts session metadata 
  (film_id, prompt_version, totals, notes)
- Appends one row to `EVAL_SCORES.md` in repo root
- Format: markdown table with columns: date, prompt_version, 
  captured_pct, missed_pct, hallucinated_pct, total_claims, notes
- Also writes JSON sidecar `EVAL_SCORES.jsonl` for machine-readable 
  trend analysis
- Both written in same call

**8. R12: Disk snapshot of graded report (2h)**
- Same endpoint as R7 writes 
  `eval_snapshots/{film_id}_{prompt_version}_{ISO8601}.json`
- Contains: report text, ground-truth doc reference, every 
  per-claim verdict + correction
- Plain file write — no R2 needed for internal data

### DAY 4 (Sat May 23)

**9. R-Integration: end-to-end testing pass (4-6h)**
- Pick a generated report (film 01 at v1.6 — the only one currently 
  run)
- Load ground truth, walk through all claims, submit
- Verify: (a) N rows in corrections DB, (b) one new row in 
  EVAL_SCORES.md, (c) one snapshot file in `eval_snapshots/`
- Stopwatch the session — target ≤40 min for a full golden film
- If not hit, identify the bottleneck and trim
- Confirm same-table writes pass cleanly alongside any production 
  coach corrections (none exist yet, so safe)
- Add Sentry instrumentation on the per-claim save endpoint

## WORKING APPROACH

- Branch: `feature/grading-ui` (already created)
- One numbered task at a time
- Update ROADMAP.md after each task completes
- Commit per task with clear message
- Open PR at end of each day so I can review

## DO NOT

- Build structured-claims extraction (R9 v2) — that's post-MVP
- Touch production coach corrections flow — keep schema compatible 
  but don't refactor
- Add features beyond what's listed above
- Pretty up the UI beyond basic Tailwind grid + buttons. Function first.

## WHEN DONE

- All 9 items complete, integration test passed
- Tommy can grade a golden film in 40 minutes or less
- Ready to grade films 1-5 at v1.6 baseline starting Sat afternoon
