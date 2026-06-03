-- Stage A "possession log" — a STANDALONE offensive-possession charting pass.
--
-- This table is the perception/truth layer. It is graded separately from the
-- report and is intentionally DECOUPLED from the report pipeline:
--   * It does NOT reference report_sections, film_analysis_cache, or
--     film_chunks.extraction_output (the Prompt 0A/0B path).
--   * It does NOT participate in films.status or run_chunk_synthesis gating.
--   * It is written only by the manual `run_possession_log` pass.
--
-- Append-only. A single pass over one film shares one run_id; re-running the
-- pass writes a brand-new run_id. Prior rows are NEVER overwritten or deleted —
-- the newest run (max generated_at) wins at read time.

CREATE TABLE possession_logs (
  id               uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  film_id          uuid        NOT NULL REFERENCES films(id),
  run_id           uuid        NOT NULL,
  generated_at     timestamptz NOT NULL DEFAULT now(),

  chunk_index      integer     NOT NULL,
  possession_index integer     NOT NULL,   -- order within that chunk

  video_elapsed    text,                    -- "mm:ss" from start of that chunk's video
  personnel        jsonb       NOT NULL DEFAULT '[]'::jsonb,  -- array of jersey strings (may be partial)
  action_type      text,
  action_detail    text,
  situation        text,                    -- BLOB/SLOB/ATO/late_clock/end_of_period/press_break/none
  initiator        text,                    -- jersey string or 'unknown'
  screeners        jsonb       NOT NULL DEFAULT '[]'::jsonb,  -- array of jersey strings
  outcome_code     text,
  outcome_detail   text,
  boundary         text,                    -- complete/start_partial/end_partial
  confidence       text,                    -- high/medium/low
  notes            text
);

-- Group + order one pass over one film.
CREATE INDEX idx_possession_logs_run ON possession_logs(film_id, run_id, chunk_index, possession_index);
-- "Newest run wins" lookups.
CREATE INDEX idx_possession_logs_latest ON possession_logs(film_id, generated_at DESC);
