-- R6: Three-way claim classification for the grading UI.
-- Adds claim_status (captured/missed/hallucinated), backfills from is_correct,
-- locks the enum + claim_status/ai_claim/correct_claim semantic invariant at the
-- DB layer, and relaxes ai_claim NOT NULL so Missed rows can store ground-truth
-- text only. is_correct is retained for backwards compat with existing reads in
-- routers/admin.py and the frontend; drop scheduled in a follow-up migration
-- after R3 wires the new column.

-- Step 1: Add claim_status column, nullable initially so the backfill can run.
ALTER TABLE corrections ADD COLUMN claim_status text;

-- Step 2: Backfill existing rows from the legacy is_correct binary.
-- Existing data is all binary captured/hallucinated — no missed rows exist
-- because the prior schema couldn't represent them. This mapping runs exactly once.
UPDATE corrections
SET claim_status = CASE
  WHEN is_correct = true  THEN 'captured'
  WHEN is_correct = false THEN 'hallucinated'
END
WHERE claim_status IS NULL;

-- Step 3: Lock down the enum at the DB layer. App-layer validation is not enough
-- for the training data moat — a typo silently writing 'capture' would poison
-- the dataset permanently.
ALTER TABLE corrections
  ADD CONSTRAINT corrections_claim_status_valid
  CHECK (claim_status IN ('captured', 'missed', 'hallucinated'));

ALTER TABLE corrections
  ALTER COLUMN claim_status SET NOT NULL;

-- Step 4: Relax ai_claim — Missed rows have no AI text to store.
ALTER TABLE corrections ALTER COLUMN ai_claim DROP NOT NULL;

-- Step 5: Semantic invariant — bakes the meaning of claim_status into the schema.
-- captured/hallucinated: TEX produced text, so ai_claim is present.
-- missed: TEX produced nothing, so ai_claim is NULL and correct_claim holds the ground-truth text.
ALTER TABLE corrections
  ADD CONSTRAINT corrections_claim_text_present CHECK (
    (claim_status = 'captured'     AND ai_claim IS NOT NULL) OR
    (claim_status = 'hallucinated' AND ai_claim IS NOT NULL) OR
    (claim_status = 'missed'       AND ai_claim IS NULL AND correct_claim IS NOT NULL)
  );

-- Step 6: Index — pattern analyzer will GROUP BY claim_status, matching the
-- existing indexing rationale in SCHEMA.md for this table.
CREATE INDEX idx_corrections_claim_status ON corrections(claim_status);

-- Step 7: is_correct is intentionally NOT dropped. Existing reads in
-- backend/routers/admin.py (pattern analysis, list endpoint) and the frontend
-- still reference it. Application code from R3 onward writes BOTH columns on
-- insert (claim_status as source of truth; is_correct derived: captured→true,
-- hallucinated→false, missed→false). A follow-up migration after launch drops
-- is_correct once all read paths have moved over.
