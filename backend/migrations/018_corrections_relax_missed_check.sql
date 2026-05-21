-- R3+R10: two constraint changes on corrections.
--
-- 1. Relax the corrections_claim_text_present CHECK added in migration 017.
--    The v1 sentence-split walker (R9) classifies *TEX-produced* sentences
--    as captured/missed/hallucinated. For Missed in that workflow, ai_claim
--    holds the TEX sentence the grader pressed M on (the anchor for "this
--    whole area should have included X"); correct_claim is genuinely
--    optional. The 017 constraint assumed a structured-claims walker that
--    enumerates missed claims abstractly — that's a v2 concern.
--    The replacement constraint enforces only the minimum semantic guard
--    that holds in every workflow: a row must have something to anchor the
--    training signal. Finer-grained checks live in routers/admin.py.
--
-- 2. Lock down the category enum at the DB layer, matching the pattern
--    migration 017 set for claim_status. The training data moat depends on
--    a clean enum here — a typo silently writing 'set_id' would poison the
--    pattern-analyzer rates permanently. Adds 'walker_v1' to the enum so
--    R3+R10's walker writes (which lack the per-claim error-type context
--    the legacy single-correction form had) can be cleanly segregated from
--    manually-categorized rows in by_category analysis.

ALTER TABLE corrections DROP CONSTRAINT corrections_claim_text_present;

ALTER TABLE corrections
  ADD CONSTRAINT corrections_claim_text_present CHECK (
    ai_claim IS NOT NULL OR correct_claim IS NOT NULL
  );

ALTER TABLE corrections
  ADD CONSTRAINT corrections_category_valid CHECK (
    category IN (
      'set_identification',
      'player_attribution',
      'frequency_count',
      'tendency',
      'coverage_type',
      'personnel_evaluation',
      'strategic_reasoning',
      'walker_v1'
    )
  );
