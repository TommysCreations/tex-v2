# TEX v2 — Launch Checklist v2 (May 19 → June 7, 2026)

**Updated 2026-05-19** — Grading UI scope revised after audit 
(GRADING_UI_AUDIT.md showed 38% coverage, not 60%; build now sized 
for 27-38 hours / ~4 focused days).

**North Star:** All TRAINING.md §5 quality + product floors green. 
5 golden films scored. Grading UI built. Stripe live. 3-5 coaches 
onboarded at $49.99/report (first report free).

---

## 🎯 LAUNCH CRITERIA (TRAINING.md §5 — keep visible)

### Quality floors (per golden set scoring)
- [ ] No section in any golden-set report contains more than 2 hallucinated claims per page
- [ ] Per-section CAPTURED / (CAPTURED + MISSED) accuracy ≥ 70% on top 3 sections per film
- [ ] Sections 5 and 6 (Game Plan, Adjustments) never contradict sections 1-4
- [ ] Every rostered player has a player page with player-specific content

### Product floors (launch-critical, not AI)
- [ ] Reports generate in ≤ 15 minutes end-to-end (upload to PDF)
- [ ] No more than 1 failed report per 20 attempts across the 5 golden films
- [ ] Training mode (Phase 4) functional — corrections save to corrections table
- [ ] Payment flow real — Stripe live keys active, coaches can pay and receive credits

### Launch terms
- [ ] Ship to 3-5 coaches at $49.99 per report
- [ ] First report free per account
- [ ] Monthly improvement cadence promise to coaches

---

## DECISIONS LOCKED (2026-05-19)

- ✅ **Build approach:** Option 1 — real grading UI, properly sized (not v0 shortcut)
- ✅ **R6 schema:** Option A — add `claim_status` column, proper migration
- ✅ **R9 claim walker:** sentence-split v1 (4h), upgrade to structured-claims post-MVP
- ✅ **Skip:** structured-claims prompt redesign, RLHF preference grading, multi-grader workflows, blind set support (all post-MVP)

---

## TODAY — Tuesday May 19 (complete)
- [x] Identify which films are run at v1.6 (1 of 5: `e21a5d8a`)
- [x] Decision: re-run all 5 for clean baseline (deferred to Fri before grading)
- [x] Delete existing v1.6 cache row for `e21a5d8a`
- [x] Re-read TRAINING.md §4.5 fully
- [x] Re-read TRAINING.md §5 fully
- [x] Audit `/admin` UI — Claude Code produced GRADING_UI_AUDIT.md (38% coverage)
- [x] Open branch: `feature/grading-ui`
- [x] Make build decisions (Option 1, R6=A, R9=sentence-split)
- [x] Write decisions block at top of GRADING_UI_AUDIT.md
- [x] Set stopping point note for tomorrow

---

## WEEK 1 — May 20-25: Grading UI build + grade 5 films at v1.6

### Wednesday May 20 (full day, ~8-10 hrs) — Foundation
- [ ] **R6:** Schema migration — add `claim_status` column, `ai_claim` nullable (1-2h)
- [ ] **R13:** New admin endpoint — GET `/admin/reports/{report_id}` returns full report content (3h)
- [ ] **R8:** Ground-truth loader — backend reads `golden_set/{slug}/ground_truth.md`, frontend dropdown (3-5h)
- [ ] Commit + PR

### Thursday May 21 (full day, ~11-14 hrs) — Build the grading experience
- [ ] **R7:** Side-by-side layout at `/admin/grade/[report_id]` — two-pane, markdown-rendered (4-6h)
- [x] **R9:** Sentence-split claim walker with [Captured][Missed][Hallucinated] buttons + keyboard shortcuts (4h) — **PR #43 merged**
- [x] **R3+R10:** Per-claim save wiring — extend POST `/admin/corrections` for `claim_status`, auto-populate context (3-4h) — **PR #44 merged**
- [ ] **R9 visual-state polish:** highlight previously-selected classification on back-navigation (neutral base / saturated active per tone) — follow-up PR on `feature/grading-ui`, awaiting Tommy smoke test
- [ ] Commit + PR

### Friday May 22 (evening, ~4-5 hrs) — Outputs
- [ ] **R11:** EVAL_SCORES.md auto-writer (markdown + JSONL sidecar) (2-3h)
- [ ] **R12:** Disk snapshot of graded report to `eval_snapshots/{film_id}_{prompt_version}_{ts}.json` (2h)
- [ ] Trigger pipeline re-runs on remaining 4 golden films at v1.6 (Fri night so Sat is clean)
- [ ] Commit + PR

### Saturday May 23 (full day) — Integration + first grade
- [ ] **Integration test** — grade film 01 at v1.6 through the UI end-to-end (4-6h)
- [ ] Verify: corrections DB rows + EVAL_SCORES.md entry + snapshot file
- [ ] Stopwatch the session — target ≤40 min per film
- [ ] If >40 min: identify bottleneck and trim
- [ ] If clean: grade films 2-3 the same afternoon

### Sunday May 24 (full day) — Finish baseline
- [ ] Grade films 4-5 at v1.6
- [ ] Write one-page summary at EOD: which §5 floors are green, which are red
- [ ] Identify top 3 systematic errors across the 5 films
- [ ] Decide which error to fix first in Monday's correction cycle

### Monday May 25 — Memorial Day (full day if off)
- [ ] Confirm off
- [ ] First prompt correction cycle: ONE change at a time
- [ ] Bump prompt to v1.7
- [ ] Re-run only affected films/sections
- [ ] Re-grade only affected sections
- [ ] Update EVAL_SCORES.md with before/after
- [ ] If time: second correction cycle

### End of Week 1 — Checkpoint
- [ ] Grading UI built (all 9 items)
- [ ] 5 films graded at v1.6 baseline
- [ ] Quality floor gaps quantified in EVAL_SCORES.md
- [ ] 1-2 correction cycles complete
- [ ] EVAL_SCORES.md shows trajectory

---

## WEEK 2 — May 26-31: Eval grind + launch-blocking fixes

### Tuesday May 26 (evening, ~3 hrs)
- [ ] Correction cycle: one surgical prompt change
- [ ] Re-run affected films/sections
- [ ] Update EVAL_SCORES.md

### Wednesday May 27 (evening, ~3 hrs)
- [ ] Correction cycle
- [ ] Update EVAL_SCORES.md

### Thursday May 28 (evening, ~3 hrs) — Launch-blockers
- [ ] Fix `validate_env()` scope — check ALL required env vars
- [ ] Fix migration ordering / off-by-one between docs and actual schema
- [ ] Close Issue #34 — server-side upload validation gap

### Friday May 29 (evening, ~3 hrs)
- [ ] Correction cycle
- [ ] Update EVAL_SCORES.md
- [ ] Close Issue #35 — verify Gemini and Claude pricing in COSTS.md (~30 min)

### Saturday May 30 (full day)
- [ ] 2-3 correction cycles
- [ ] Focus on whichever quality floor is most red
- [ ] Update EVAL_SCORES.md after each

### Sunday May 31 (full day) — Honest re-assessment
- [ ] Final correction cycles of Week 2
- [ ] On track for all §5 floors green by June 5?
- [ ] If YES: continue to Week 3 as planned
- [ ] If NO: is gap prompt engineering vs. structural? Write decision note.

### End of Week 2 — Checkpoint
- [ ] Drift-report launch-blockers fixed
- [ ] Issues #34 and #35 closed
- [ ] 5-8 correction cycles done since baseline
- [ ] Quality floors mostly or entirely green

---

## WEEK 3 — June 1-5 (full week off): Close eval, harden, prepare launch

### Monday June 1 (full day)
- [ ] Final correction cycles — push remaining quality floors to green
- [ ] Time a fresh run end-to-end — confirm ≤15 min upload → PDF
- [ ] Run each golden film 4x to measure failure rate (target ≤1 in 20)
- [ ] Fix any systematic failure causes found

### Tuesday June 2 (full day)
- [ ] Switch Stripe from test mode to live keys
- [ ] End-to-end real $1 transaction (refund after)
- [ ] Draft Terms of Service (template-based)
- [ ] Draft Privacy Policy
- [ ] Draft Refund Policy
- [ ] First-report-free credit logic working

### Wednesday June 3 (full day)
- [ ] Walk coach onboarding flow as first-timer
- [ ] Identify and fix top 3 confusion/break points
- [ ] Confirm PDF output is polished
- [ ] Pick first 3-5 coaches to onboard
- [ ] Draft personal outreach message to each

### Thursday June 4 (full day)
- [ ] Production-readiness check
- [ ] Deploy or confirm current infra
- [ ] Document rollback procedure
- [ ] Wire minimum observability (Slack webhook on report-failure)
- [ ] Confirm first-report-free credit applies correctly

### Friday June 5 (full day) — Soft launch
- [ ] Onboard COACH #1 only
- [ ] Watch the entire flow in real-time
- [ ] Fix whatever breaks
- [ ] Confirm coach #1 receives a report they're happy with

### End of Week 3 — Checkpoint
- [ ] All §5 quality floors green
- [ ] All §5 product floors green
- [ ] Stripe live, policies posted
- [ ] Coach #1 fully onboarded

---

## LAUNCH WEEKEND — June 6-7

### Saturday June 6
- [ ] Onboard COACH #2
- [ ] Onboard COACH #3
- [ ] Watch flows, fix breaks
- [ ] Collect qualitative feedback

### Sunday June 7 — LAUNCH TARGET
- [ ] Onboard COACH #4
- [ ] Onboard COACH #5
- [ ] All §5 floors confirmed green in production
- [ ] Corrections accumulating from real coaches
- [ ] EOD: launch retrospective

### Launch confirmed when:
- [ ] 3-5 coaches paying (or free first report active)
- [ ] TEX live in production
- [ ] EVAL_SCORES.md shows all §5 floors green
- [ ] Real corrections accumulating from real coaches
- [ ] Monthly improvement cadence committed in writing

---

## ❌ EXPLICITLY DEFERRED (not before June 7)

- [ ] ~~Subscription tiers (#30)~~
- [ ] ~~Full Sentry / Datadog / PostHog (#29)~~
- [ ] ~~Cloud Run / full Phase 5 hardening~~
- [ ] ~~Cursor extensions~~
- [ ] ~~Branch protection fix (#36)~~
- [ ] ~~`fallback_events` table wire-up (#27)~~
- [ ] ~~#28 v1.6 → v2.0 prompt doc formalization~~
- [ ] ~~Vertex migration (D-011)~~
- [ ] ~~Structured-claims claim walker (R9 v2)~~
- [ ] ~~Non-launch-blocking doc drift~~

---

## ⚠️ RISKS TO TRACK

- [ ] **Risk 1:** Grading UI takes >4 days (Wed-Thu-Fri-Sat)
  - [ ] Mitigation: if behind by Thu EOD, drop R12 (disk snapshot) and ship without it
  - [ ] Trigger: if 3 build days in and <50% of items complete

- [ ] **Risk 2:** Quality floors don't close with prompt engineering alone
  - [ ] Mitigation: timebox prompt engineering to end of Week 2
  - [ ] Trigger: if Sun May 31 shows no movement after 5+ cycles

- [ ] **Risk 3:** First coach uploads break something unforeseen
  - [ ] Mitigation: Friday June 5 = ONE coach only, not three
  - [ ] Trigger: if Coach #1 flow has any blocking failure

---

## 📝 NOTES

```
[2026-05-19] Audit complete: GRADING_UI_AUDIT.md shows 38% coverage 
of TRAINING.md §4.5. 9 build items identified, estimated 27-38 hours. 
Build sized to Wed-Thu-Fri evening-Sat. Decisions locked: Option 1, 
R6=A, R9=sentence-split v1.
```
