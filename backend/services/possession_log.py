"""Stage A possession-log pass — a STANDALONE offensive-possession charting run.

This is a second, independent consumer of the SAME chunk videos the report
pipeline uses. It is the perception/truth layer and is graded separately from
the report. It is deliberately decoupled from the report path:

  * Reads only:  films.team_id, the scouted team's seeded name (teams.name),
                 the seeded roster (roster_players, pre-film seed source only),
                 and read-only chunk metadata from film_chunks (chunk_index,
                 r2_chunk_key, gemini_file_uri, gemini_file_expires_at,
                 gemini_file_state).
                 It NEVER reads films.status, film_chunks.extraction_output,
                 the Prompt 0B synthesis input, film_analysis_cache, or
                 report_sections.
  * Writes only: append-only rows into possession_logs.
  * It NEVER sets films.status, NEVER gates run_chunk_synthesis or
    generate_report, and NEVER takes the film-id advisory lock.

Video source — read-only reuse of the chunk videos:
  Gemini File API uploads expire ~48h after upload, so for a manual
  calibration run days later the per-chunk URIs in film_chunks are usually
  dead. This pass therefore resolves each chunk's video without mutating any
  shared state:
    - If the chunk's existing Gemini URI is still live (state 'active' AND not
      past its expiry window), it is reused as-is — a pure read.
    - Otherwise the durable R2 chunk copy is re-uploaded to a FRESH,
      pass-owned Gemini file, used for this run, and deleted afterward. The
      new URI is NEVER written back to film_chunks, so the report path's URI
      state is left untouched.
  If neither a live URI nor an R2 copy exists, the chunk's video has been
  garbage-collected and the pass reports it rather than fabricating data.

Manual-trigger only. Not wired into any live enqueue.
See scripts/run_possession_log.py.
"""

import json
import logging
import os
import uuid
from datetime import UTC, datetime

from services.ai.router import get_ai_provider
from services.db import get_connection
from services.gemini_files import delete_gemini_file, upload_to_gemini
from services.prompts import load_prompt
from services.r2 import download_from_r2
from services.rate_limit import acquire_gemini_slot
from services.roster_format import format_roster_for_prompt

log = logging.getLogger(__name__)

# Section label used for the AI router's video call. The pass is a separate
# perception layer, so it does not reuse any report section_type. The prompt
# itself lives in backend/prompts/possession_log.txt (loaded via load_prompt),
# matching how the 0A/0B and section prompts are stored.
SECTION_TYPE = "possession_log"

# Re-upload from R2 if the existing Gemini URI expires within this window
# (or has no expiry recorded). Mirrors uri_expiry's 1-hour safety margin.
_EXPIRY_MARGIN_SECONDS = 3600


def build_prompt(scouted_team_name: str, opponent_team_name: str, roster_text: str) -> str:
    """Load the Stage A extraction prompt and inject the per-game parameters.

    The prompt template (backend/prompts/possession_log.txt) is parameterized:
    {scouted_team} and {opponent} drive every team reference, and {roster} is
    the seeded pre-film roster for the scouted team. The charting discipline is
    fixed in the template and never varies per game.
    """
    template, _version = load_prompt(SECTION_TYPE)
    return template.format(
        scouted_team=scouted_team_name,
        opponent=opponent_team_name,
        roster=roster_text,
    )


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _strip_json_fences(text: str) -> str:
    """Remove a leading ```json / ``` fence if the model added one anyway."""
    t = text.strip()
    if t.startswith("```"):
        # Drop the first fence line and a trailing fence if present.
        lines = t.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def parse_possessions(raw_text: str) -> list[dict]:
    """Parse the model's JSON array. Raises ValueError on malformed output."""
    cleaned = _strip_json_fences(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}") from e
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array of possessions, got {type(data).__name__}")
    out = []
    for item in data:
        if isinstance(item, dict):
            out.append(item)
        else:
            log.warning("possession_log: skipping non-object array element: %r", item)
    return out


def _as_jersey_array(value) -> list[str]:
    """Coerce personnel / screeners into a JSON array of jersey strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    # A single value or comma-joined string — wrap defensively.
    return [str(value)]


def _row_values(
    film_id: str, run_id: str, chunk_index: int, possession_index: int, p: dict
) -> tuple:
    """Map one parsed possession dict to possession_logs column values."""
    return (
        film_id,
        run_id,
        chunk_index,
        possession_index,
        (p.get("video_elapsed") or None),
        json.dumps(_as_jersey_array(p.get("personnel"))),
        (p.get("action_type") or None),
        (p.get("action_detail") or None),
        (p.get("situation") or None),
        (p.get("initiator") or None),
        json.dumps(_as_jersey_array(p.get("screeners"))),
        (p.get("outcome_code") or None),
        (p.get("outcome_detail") or None),
        (p.get("boundary") or None),
        (p.get("confidence") or None),
        (p.get("notes") or None),
    )


_INSERT_SQL = (
    "INSERT INTO possession_logs "
    "(film_id, run_id, chunk_index, possession_index, video_elapsed, personnel, "
    "action_type, action_detail, situation, initiator, screeners, outcome_code, "
    "outcome_detail, boundary, confidence, notes) "
    "VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s)"
)


# ---------------------------------------------------------------------------
# Video resolution (read-only — never writes film_chunks)
# ---------------------------------------------------------------------------


def _uri_is_live(state: str | None, expires_at: datetime | None) -> bool:
    """True if the chunk's existing Gemini URI can be reused without re-upload."""
    if state != "active":
        return False
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at.timestamp() > datetime.now(UTC).timestamp() + _EXPIRY_MARGIN_SECONDS


def _resolve_chunk_uri(
    film_id: str,
    chunk_index: int,
    r2_chunk_key: str | None,
    existing_uri: str | None,
    state: str | None,
    expires_at: datetime | None,
    bucket: str,
    tmp_files: list[str],
    ephemeral_uris: list[str],
) -> str:
    """Return a usable Gemini video URI for this chunk WITHOUT mutating film_chunks.

    Reuses the live URI when possible; otherwise re-uploads the durable R2 copy
    to a fresh, pass-owned Gemini file (tracked for cleanup by the caller).
    """
    if _uri_is_live(state, expires_at) and existing_uri:
        log.info(
            "possession_log: reusing live Gemini URI for film %s chunk %d", film_id, chunk_index
        )
        return existing_uri

    if not r2_chunk_key:
        raise RuntimeError(
            f"film {film_id} chunk {chunk_index}: no live Gemini URI and no R2 key — "
            f"chunk video is unrecoverable"
        )

    local_path = f"/tmp/{film_id}_poss_chunk_{chunk_index:03d}.mp4"
    tmp_files.append(local_path)
    log.info(
        "possession_log: URI dead — re-uploading R2 chunk %d (film %s) to a fresh Gemini file",
        chunk_index,
        film_id,
    )
    download_from_r2(bucket, r2_chunk_key, local_path)
    result = upload_to_gemini(local_path)
    uri = str(result["uri"])
    ephemeral_uris.append(uri)
    return uri


# ---------------------------------------------------------------------------
# The pass
# ---------------------------------------------------------------------------


def run_possession_log(
    film_id: str,
    opponent_team_name: str,
    scouted_team_name: str | None = None,
) -> dict:
    """Chart every offensive possession across one film's chunks, append-only.

    Args:
        film_id: the film to chart.
        opponent_team_name: the opposing team's name (not stored structurally,
            so it must be supplied by the caller).
        scouted_team_name: the scouted team's name. If omitted, it is derived
            read-only from the film's seeded team (films.team_id -> teams.name).

    The seeded roster handed to Gemini is sourced ONLY from the pre-film seed
    data (roster_players for the film's team), never from any ground-truth or
    film_watch_notes source.

    Returns a summary dict:
        {
          "film_id": ..., "run_id": ..., "team_id": ...,
          "scouted_team_name": ..., "opponent_team_name": ...,
          "chunks": [{"chunk_index": 0, "possessions": 7, "status": "ok"}, ...],
          "total_possessions": 23,
          "failed_chunks": [2],
        }

    Read-only on every existing table. Writes only append-only possession_logs
    rows. Never touches films.status or the report pipeline.
    """
    run_id = str(uuid.uuid4())
    bucket = os.environ["CLOUDFLARE_R2_BUCKET_FILMS"]
    tmp_files: list[str] = []
    ephemeral_uris: list[str] = []

    log.info("possession_log: starting run %s for film %s", run_id, film_id)

    try:
        # 1. Read team_id (NOT status) + team name and the chunk metadata —
        #    all read-only. teams.name is the scouted team's seeded name.
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT f.team_id, t.name FROM films f "
                    "LEFT JOIN teams t ON t.id = f.team_id WHERE f.id = %s",
                    (film_id,),
                )
                film_row = cur.fetchone()
                if not film_row:
                    raise RuntimeError(f"Film not found: {film_id}")
                team_id = str(film_row[0]) if film_row[0] else None
                seeded_team_name = film_row[1]

                cur.execute(
                    "SELECT chunk_index, r2_chunk_key, gemini_file_uri, "
                    "gemini_file_expires_at, gemini_file_state "
                    "FROM film_chunks WHERE film_id = %s ORDER BY chunk_index",
                    (film_id,),
                )
                chunk_rows = cur.fetchall()
        finally:
            conn.close()

        if not chunk_rows:
            raise RuntimeError(f"No chunks found for film {film_id}")

        # Scouted team name: caller override, else the film's seeded team name.
        resolved_scouted = scouted_team_name or seeded_team_name
        if not resolved_scouted:
            raise RuntimeError(
                f"film {film_id}: no scouted team name (film has no seeded team) — "
                f"pass scouted_team_name explicitly"
            )

        # Seeded roster — pre-film seed source only (roster_players for the team).
        roster_text = format_roster_for_prompt(team_id) if team_id else "(no roster data available)"
        prompt = build_prompt(resolved_scouted, opponent_team_name, roster_text)
        log.info(
            "possession_log: scouted=%s opponent=%s for film %s",
            resolved_scouted,
            opponent_team_name,
            film_id,
        )

        provider = get_ai_provider()
        chunk_summaries: list[dict] = []
        failed_chunks: list[int] = []
        total_possessions = 0

        # 2. One Gemini 2.5 Pro video call per chunk.
        for chunk_index, r2_chunk_key, existing_uri, expires_at, state in chunk_rows:
            try:
                gemini_uri = _resolve_chunk_uri(
                    film_id,
                    chunk_index,
                    r2_chunk_key,
                    existing_uri,
                    state,
                    expires_at,
                    bucket,
                    tmp_files,
                    ephemeral_uris,
                )

                acquire_gemini_slot("gemini-2.5-pro")
                log.info("possession_log: charting film %s chunk %d", film_id, chunk_index)
                raw = provider.analyze_video(
                    uris=[gemini_uri],
                    prompt=prompt,
                    section_type=SECTION_TYPE,
                )
                possessions = parse_possessions(raw)

                # 3. Append rows for this chunk under the shared run_id.
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        for pi, p in enumerate(possessions):
                            cur.execute(
                                _INSERT_SQL,
                                _row_values(film_id, run_id, chunk_index, pi, p),
                            )
                    conn.commit()
                finally:
                    conn.close()

                total_possessions += len(possessions)
                chunk_summaries.append(
                    {"chunk_index": chunk_index, "possessions": len(possessions), "status": "ok"}
                )
                log.info(
                    "possession_log: film %s chunk %d charted %d possessions",
                    film_id,
                    chunk_index,
                    len(possessions),
                )
            except Exception as chunk_exc:
                # One chunk failing must not lose the chunks that succeeded —
                # the run is append-only and grouped by run_id.
                log.exception(
                    "possession_log: chunk %d failed for film %s: %s",
                    chunk_index,
                    film_id,
                    chunk_exc,
                )
                failed_chunks.append(chunk_index)
                chunk_summaries.append(
                    {"chunk_index": chunk_index, "possessions": 0, "status": f"error: {chunk_exc}"}
                )

        return {
            "film_id": film_id,
            "run_id": run_id,
            "team_id": team_id,
            "scouted_team_name": resolved_scouted,
            "opponent_team_name": opponent_team_name,
            "chunks": chunk_summaries,
            "total_possessions": total_possessions,
            "failed_chunks": failed_chunks,
        }

    finally:
        # Delete pass-owned ephemeral Gemini files (never touches film_chunks URIs).
        for uri in ephemeral_uris:
            delete_gemini_file(uri)
        # Delete tracked /tmp files on success, failure, and crash.
        for path in tmp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                log.warning("possession_log: failed to clean up tmp file %s", path)
