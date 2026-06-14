"""Admin routes — all gated by require_admin on every request.

Per CLAUDE.md:
  - Check is_admin on every admin request, not just at login
  - Only the service role key can insert into corrections
  - corrections table is the training dataset — never soft-deleted
"""

import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models.schemas import (
    AdminReportDetail,
    AdminReportFilm,
    AdminReportSection,
    GoldenFilm,
    GroundTruthDocument,
)
from services.clerk import require_admin
from services.db import get_connection

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class CorrectionCreate(BaseModel):
    report_id: str
    film_id: str
    section_type: str
    # R3+R10: claim_status is the new source of truth. is_correct is retained
    # for backwards compatibility with reads in list/pattern endpoints and the
    # legacy single-correction form. When is_correct is omitted, it's derived
    # server-side from claim_status (captured → true, missed/hallucinated → false).
    claim_status: Literal["captured", "missed", "hallucinated"]
    ai_claim: str | None = None
    is_correct: bool | None = None
    correct_claim: str | None = None
    category: str
    confidence: str = "high"
    prompt_version: str
    admin_notes: str | None = None
    phase: int = 1
    game_count: int | None = None


class CreditGrant(BaseModel):
    credits: int


# Canonical section order from PROMPTS.md. Sections are returned in this order;
# missing rows are not fabricated — the frontend detects gaps by section_type.
CANONICAL_SECTION_ORDER = [
    "offensive_sets",
    "defensive_schemes",
    "pnr_coverage",
    "player_pages",
    "game_plan",
    "adjustments_practice",
]


# Golden-set ground-truth files live outside the backend tree. In the Docker
# dev stack ./golden_set is mounted read-only at /golden_set. Production
# (Cloud Run) will need a different strategy — bake into image or pull from
# R2 — per GRADING_UI_AUDIT.md ("productionize later if needed").
GOLDEN_SET_ROOT = Path(os.environ.get("GOLDEN_SET_ROOT", "/golden_set")).resolve()
# Slug accepted from URL path. Restricted to characters that can appear in a
# directory name we control. Anything outside this set is rejected with 400
# before any filesystem access.
GOLDEN_SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


# Slugs whose algorithmic display name needs an acronym override. Title-case
# alone can't tell 'bbe' (acronym) from 'team' (word). Keep this list short
# and only add entries when the algorithmic output is wrong.
DISPLAY_NAME_OVERRIDES = {
    "film_01_bbe_vs_team_durant": "Film 01 — BBE vs Team Durant",
    "film_02_rebels_vs_az_unity": "Film 02 — Rebels vs AZ Unity",
}


def _slug_to_display_name(slug: str) -> str:
    """Humanize a golden-set slug for display.

    `film_NN_x_vs_y` → `Film NN — X vs Y`. Title-cases every token except
    'vs', which stays lowercase. Acronyms (BBE, AZ) live in
    DISPLAY_NAME_OVERRIDES — title-case alone can't disambiguate them.
    """
    if slug in DISPLAY_NAME_OVERRIDES:
        return DISPLAY_NAME_OVERRIDES[slug]
    tokens = slug.split("_")
    if len(tokens) < 3 or tokens[0].lower() != "film":
        return slug.replace("_", " ")
    rest = " ".join(t if t == "vs" else t.capitalize() for t in tokens[2:])
    return f"Film {tokens[1]} — {rest}"


# ---------------------------------------------------------------------------
# R8 — GET /admin/golden-set (grading UI)
# ---------------------------------------------------------------------------


@router.get("/golden-set", response_model=list[GoldenFilm])
async def list_golden_films(user: dict = Depends(require_admin)):
    """List available golden films — one entry per subdirectory containing
    a `ground_truth.md` file.
    """
    if not GOLDEN_SET_ROOT.is_dir():
        return []
    films: list[GoldenFilm] = []
    for entry in sorted(GOLDEN_SET_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if not (entry / "ground_truth.md").is_file():
            continue
        slug = entry.name
        if not GOLDEN_SLUG_PATTERN.match(slug):
            # Skip oddly-named directories rather than expose them. They
            # cannot be fetched through the GET-by-slug endpoint anyway.
            continue
        films.append(GoldenFilm(slug=slug, display_name=_slug_to_display_name(slug)))
    return films


# ---------------------------------------------------------------------------
# R8 — GET /admin/golden-set/{film_slug}/ground-truth (grading UI)
# ---------------------------------------------------------------------------


@router.get(
    "/golden-set/{film_slug}/ground-truth",
    response_model=GroundTruthDocument,
)
async def get_ground_truth(
    film_slug: str,
    user: dict = Depends(require_admin),
):
    """Return the raw markdown of `golden_set/{film_slug}/ground_truth.md`.

    Frontend renders the markdown — this endpoint does no parsing.
    """
    if not GOLDEN_SLUG_PATTERN.match(film_slug):
        raise HTTPException(status_code=400, detail="Invalid film_slug")

    candidate = (GOLDEN_SET_ROOT / film_slug).resolve()
    # Defense in depth: even with the regex, confirm the resolved path is
    # still inside GOLDEN_SET_ROOT before any read.
    if candidate != GOLDEN_SET_ROOT and GOLDEN_SET_ROOT not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid film_slug")

    if not candidate.is_dir():
        raise HTTPException(status_code=404, detail="Golden film not found")

    ground_truth_path = candidate / "ground_truth.md"
    if not ground_truth_path.is_file():
        raise HTTPException(status_code=404, detail="ground_truth.md not found")

    content = ground_truth_path.read_text(encoding="utf-8")
    return GroundTruthDocument(slug=film_slug, content=content)


# ---------------------------------------------------------------------------
# R13 — GET /admin/reports/{report_id} (grading UI)
# ---------------------------------------------------------------------------


@router.get("/reports/{report_id}", response_model=AdminReportDetail)
async def get_admin_report_detail(
    report_id: UUID,
    user: dict = Depends(require_admin),
):
    """Return full report content + per-section metadata + films list.

    Read-only, admin-gated. Consumed by the grading UI (R7 side-by-side view).
    No user_id scoping — admins see everything.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT r.id, r.user_id, r.team_id, t.name, r.status, "
                "r.prompt_version, r.created_at, r.completed_at "
                "FROM reports r JOIN teams t ON t.id = r.team_id "
                "WHERE r.id = %s AND r.deleted_at IS NULL",
                (str(report_id),),
            )
            report_row = cur.fetchone()
            if not report_row:
                raise HTTPException(status_code=404, detail="Report not found")

            cur.execute(
                "SELECT f.id, f.file_name "
                "FROM report_films rf "
                "JOIN films f ON f.id = rf.film_id "
                "WHERE rf.report_id = %s "
                "ORDER BY rf.created_at",
                (str(report_id),),
            )
            film_rows = cur.fetchall()

            cur.execute(
                "SELECT section_type, status, content, model_used, prompt_version, "
                "chunk_count, tokens_input, tokens_output, generation_time_seconds, "
                "error_message "
                "FROM report_sections "
                "WHERE report_id = %s "
                "ORDER BY array_position(%s::text[], section_type)",
                (str(report_id), CANONICAL_SECTION_ORDER),
            )
            section_rows = cur.fetchall()
    finally:
        conn.close()

    return AdminReportDetail(
        report_id=str(report_row[0]),
        user_id=str(report_row[1]),
        team_id=str(report_row[2]),
        team_name=report_row[3],
        status=report_row[4],
        report_prompt_version=report_row[5],
        created_at=report_row[6],
        completed_at=report_row[7],
        films=[AdminReportFilm(film_id=str(r[0]), file_name=r[1]) for r in film_rows],
        sections=[
            AdminReportSection(
                section_type=r[0],
                status=r[1],
                content=r[2],
                model_used=r[3],
                prompt_version=r[4],
                chunk_count=r[5],
                tokens_input=r[6],
                tokens_output=r[7],
                generation_time_seconds=r[8],
                error_message=r[9],
            )
            for r in section_rows
        ],
    )


# ---------------------------------------------------------------------------
# POST /admin/films/{film_id}/retry — re-enqueue process_film for a failed
# film without forcing the coach to re-upload. R2 object is still there;
# only DB state needs to be reset.
# ---------------------------------------------------------------------------


@router.post("/films/{film_id}/retry", status_code=202)
async def retry_film_admin(
    film_id: str,
    user: dict = Depends(require_admin),
):
    """Admin-only: re-process a film stuck in status='error'.

    Only allowed when the film is currently errored AND r2_key is populated
    — otherwise there's nothing to retry against. Resets the processing
    state columns (gemini_processing_status, chunk_count, synthesis_failed,
    error_message) so the worker starts from a clean slate.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, r2_key FROM films WHERE id = %s AND deleted_at IS NULL",
                (film_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Film not found")

            current_status, r2_key = row[0], row[1]
            if current_status != "error":
                raise HTTPException(
                    status_code=409,
                    detail=f"Film status is '{current_status}', retry only allowed on 'error'",
                )
            if not r2_key:
                raise HTTPException(
                    status_code=400,
                    detail="Film has no r2_key — nothing to retry against",
                )

            cur.execute(
                "UPDATE films SET status = 'uploaded', "
                "gemini_processing_status = NULL, chunk_count = NULL, "
                "synthesis_failed = FALSE, error_message = NULL, "
                "updated_at = now() "
                "WHERE id = %s",
                (film_id,),
            )
        conn.commit()
    finally:
        conn.close()

    from tasks.film_processing import process_film

    process_film.delay(film_id)

    logger.info(
        "Admin film retry enqueued",
        extra={"film_id": film_id, "admin_id": str(user["id"])},
    )
    return {
        "film_id": film_id,
        "status": "uploaded",
        "message": "Retry enqueued",
    }


# ---------------------------------------------------------------------------
# 4.2 — GET /admin/corrections
# ---------------------------------------------------------------------------


@router.get("/corrections")
async def list_corrections(
    section_type: str | None = Query(None),
    prompt_version: str | None = Query(None),
    category: str | None = Query(None),
    is_correct: bool | None = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    user: dict = Depends(require_admin),
):
    """List corrections, filterable by section, version, category, correctness."""
    conditions = []
    params: list = []

    if section_type:
        conditions.append("section_type = %s")
        params.append(section_type)
    if prompt_version:
        conditions.append("prompt_version = %s")
        params.append(prompt_version)
    if category:
        conditions.append("category = %s")
        params.append(category)
    if is_correct is not None:
        conditions.append("is_correct = %s")
        params.append(is_correct)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT id, report_id, film_id, section_type, ai_claim, "
                f"is_correct, correct_claim, category, confidence, "
                f"prompt_version, admin_notes, created_at "
                f"FROM corrections {where} "
                f"ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (*params, limit, offset),
            )
            rows = cur.fetchall()

            cur.execute(f"SELECT COUNT(*) FROM corrections {where}", params)
            total = cur.fetchone()[0]
    finally:
        conn.close()

    return {
        "corrections": [
            {
                "id": str(r[0]),
                "report_id": str(r[1]),
                "film_id": str(r[2]),
                "section_type": r[3],
                "ai_claim": r[4],
                "is_correct": r[5],
                "correct_claim": r[6],
                "category": r[7],
                "confidence": r[8],
                "prompt_version": r[9],
                "admin_notes": r[10],
                "created_at": r[11].isoformat() if r[11] else None,
            }
            for r in rows
        ],
        "total": total,
    }


# ---------------------------------------------------------------------------
# 4.3 — POST /admin/corrections
# ---------------------------------------------------------------------------

VALID_SECTION_TYPES = {
    "offensive_sets",
    "defensive_schemes",
    "pnr_coverage",
    "player_pages",
    "game_plan",
    "adjustments_practice",
}
VALID_CATEGORIES = {
    "set_identification",
    "player_attribution",
    "frequency_count",
    "tendency",
    "coverage_type",
    "personnel_evaluation",
    "strategic_reasoning",
    # R3+R10: walker writes use 'walker_v1' because the v1 sentence-split
    # walker has no UI to elicit error-type per claim. Pattern analyzer
    # by_category treats this as a separate bucket; structured-claims v2
    # will replace it with LLM-emitted per-claim categories.
    "walker_v1",
}
VALID_CONFIDENCE = {"high", "medium", "low"}


@router.post("/corrections", status_code=201)
async def create_correction(
    body: CorrectionCreate,
    user: dict = Depends(require_admin),
):
    """Save a correction for a specific AI claim in a report section.

    R3+R10: accepts claim_status as the new source of truth. is_correct is
    derived from claim_status (captured → true, missed/hallucinated → false)
    unless the caller passes it explicitly. ai_claim is optional for Missed
    rows (some workflows don't have an AI-text anchor); correct_claim is
    always optional. App-layer validation enforces semantic invariants beyond
    what the DB CHECK constraint covers.
    """
    if body.section_type not in VALID_SECTION_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid section_type: {body.section_type}")
    if body.category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {body.category}")
    if body.confidence not in VALID_CONFIDENCE:
        raise HTTPException(status_code=400, detail=f"Invalid confidence: {body.confidence}")

    # captured/hallucinated must have an AI claim — the row's whole purpose
    # is to anchor a training signal to model-produced text.
    if body.claim_status in ("captured", "hallucinated") and not body.ai_claim:
        raise HTTPException(
            status_code=400,
            detail=f"ai_claim is required when claim_status is '{body.claim_status}'",
        )
    # captured + correct_claim is nonsensical — a confirmed claim has no
    # correction. Reject so the dataset can't accumulate ambiguous rows.
    if body.claim_status == "captured" and body.correct_claim:
        raise HTTPException(
            status_code=400,
            detail="correct_claim must be empty when claim_status is 'captured'",
        )
    # Missed needs *something* to anchor — either the TEX sentence the grader
    # pressed M on (v1 walker) or the ground-truth text (future v2). The DB
    # CHECK enforces the same minimum; this is the friendlier app-layer error.
    if body.claim_status == "missed" and not body.ai_claim and not body.correct_claim:
        raise HTTPException(
            status_code=400,
            detail="missed rows require at least one of ai_claim or correct_claim",
        )

    # Derive is_correct from claim_status if not provided; warn if the caller
    # passed an inconsistent value (keep the explicit one but flag it).
    derived_is_correct = body.claim_status == "captured"
    if body.is_correct is None:
        is_correct = derived_is_correct
    else:
        is_correct = body.is_correct
        if is_correct != derived_is_correct:
            logger.warning(
                "is_correct passed inconsistently with claim_status",
                extra={
                    "report_id": body.report_id,
                    "claim_status": body.claim_status,
                    "is_correct_explicit": body.is_correct,
                    "is_correct_derived": derived_is_correct,
                },
            )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verify report and film exist
            cur.execute("SELECT id FROM reports WHERE id = %s", (body.report_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Report not found")
            cur.execute("SELECT id FROM films WHERE id = %s", (body.film_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Film not found")

            cur.execute(
                "INSERT INTO corrections "
                "(report_id, film_id, section_type, ai_claim, claim_status, "
                "is_correct, correct_claim, category, confidence, prompt_version, "
                "admin_notes, phase, game_count) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "RETURNING id, created_at",
                (
                    body.report_id,
                    body.film_id,
                    body.section_type,
                    body.ai_claim,
                    body.claim_status,
                    is_correct,
                    body.correct_claim,
                    body.category,
                    body.confidence,
                    body.prompt_version,
                    body.admin_notes,
                    body.phase,
                    body.game_count,
                ),
            )
            row = cur.fetchone()
            correction_id = str(row[0])
            created_at = row[1]
        conn.commit()
    finally:
        conn.close()

    logger.info(
        "Correction saved",
        extra={
            "correction_id": correction_id,
            "report_id": body.report_id,
            "section_type": body.section_type,
            "claim_status": body.claim_status,
            "is_correct": is_correct,
            "category": body.category,
            "prompt_version": body.prompt_version,
            "has_correction_text": bool(body.correct_claim),
        },
    )
    return {"id": correction_id, "created_at": created_at.isoformat()}


# ---------------------------------------------------------------------------
# R11 — POST /admin/grading-sessions/complete (EVAL_SCORES.md auto-writer)
# ---------------------------------------------------------------------------

# Repo root inside the API container. docker-compose mounts the host repo
# root at /repo:rw so EVAL_SCORES.md / EVAL_SCORES.jsonl land on the host
# filesystem ready to git-add. Override via env for native (non-Docker) dev.
EVAL_SCORES_ROOT = Path(os.environ.get("EVAL_SCORES_ROOT", "/repo")).resolve()
EVAL_SCORES_MD = EVAL_SCORES_ROOT / "EVAL_SCORES.md"
EVAL_SCORES_JSONL = EVAL_SCORES_ROOT / "EVAL_SCORES.jsonl"
# R12: per-session JSON flight-recorder. Full report content + every walker
# verdict + the ground-truth reference, one file per completed session. Lives
# alongside EVAL_SCORES.md so all eval artifacts share one mount point.
EVAL_SNAPSHOTS_DIR = EVAL_SCORES_ROOT / "eval_snapshots"
SNAPSHOT_SCHEMA_VERSION = "1"

# Markdown header written once on first session. Pipes in user-supplied
# fields are escaped before render — the schema itself uses only safe chars.
EVAL_SCORES_MD_HEADER = (
    "# EVAL_SCORES.md\n"
    "\n"
    "Auto-generated by the grading UI. One row per completed grading "
    "session.\n"
    "\n"
    "| date | film_id | report_id | prompt_version | total | captured | "
    "missed | hallucinated | captured % | missed % | hallucinated % | notes |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


class GradingSessionComplete(BaseModel):
    report_id: str
    prompt_version: str
    session_started_at: datetime
    notes: str | None = None
    # R12: optional golden-film slug the grader had selected in the UI. Used
    # only to populate ground_truth_ref in the snapshot file. Validated against
    # GOLDEN_SLUG_PATTERN; anything else falls back to None ("better null
    # than wrong").
    film_slug: str | None = None


def _md_escape(s: str) -> str:
    """Escape pipes + newlines so a notes field can't break the table."""
    return s.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _pct(numerator: int, denominator: int) -> float:
    """One-decimal percentage. Zero denominator returns 0.0 (no /0 error)."""
    if denominator <= 0:
        return 0.0
    return round(100.0 * numerator / denominator, 1)


@router.post("/grading-sessions/complete")
async def complete_grading_session(
    body: GradingSessionComplete,
    user: dict = Depends(require_admin),
):
    """Roll up a completed walker session into EVAL_SCORES.md + JSONL.

    Session identity = (report_id, prompt_version, category='walker_v1',
    created_at >= session_started_at). Re-running a session writes a new
    row with the new timestamp — multiple sessions per report are
    intentional, the longitudinal record is the point.

    Skipped claims write no corrections row, so they don't enter the rollup.
    total = captured + missed + hallucinated. Percentages are relative to
    that total (each row represents one classified claim).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verify the report exists before touching the filesystem.
            cur.execute(
                "SELECT id FROM reports WHERE id = %s AND deleted_at IS NULL",
                (body.report_id,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Report not found")

            cur.execute(
                "SELECT claim_status, COUNT(*), MAX(film_id::text) "
                "FROM corrections "
                "WHERE report_id = %s "
                "  AND prompt_version = %s "
                "  AND category = 'walker_v1' "
                "  AND created_at >= %s "
                "GROUP BY claim_status",
                (body.report_id, body.prompt_version, body.session_started_at),
            )
            rows = cur.fetchall()

            counts = {"captured": 0, "missed": 0, "hallucinated": 0}
            film_id: str | None = None
            for status, count, fid in rows:
                if status in counts:
                    counts[status] = count
                if film_id is None and fid is not None:
                    film_id = fid

            # Zero-classification session: fall back to report_films for
            # film_id so the row still anchors to the film. Writes a 0/0/0
            # entry which is useful as a "session opened but nothing
            # graded" signal in the longitudinal log.
            if film_id is None:
                cur.execute(
                    "SELECT film_id::text FROM report_films "
                    "WHERE report_id = %s ORDER BY created_at LIMIT 1",
                    (body.report_id,),
                )
                row = cur.fetchone()
                film_id = row[0] if row else None

            # R12: snapshot needs the full report text + every per-claim
            # verdict from this session. Same connection, run alongside the
            # rollup queries so we don't reopen later.
            cur.execute(
                "SELECT section_type, content FROM report_sections WHERE report_id = %s",
                (body.report_id,),
            )
            section_rows = cur.fetchall()

            cur.execute(
                "SELECT section_type, claim_status, ai_claim, correct_claim, "
                "created_at "
                "FROM corrections "
                "WHERE report_id = %s "
                "  AND prompt_version = %s "
                "  AND category = 'walker_v1' "
                "  AND created_at >= %s "
                "ORDER BY created_at ASC",
                (body.report_id, body.prompt_version, body.session_started_at),
            )
            classification_rows = cur.fetchall()
    finally:
        conn.close()

    total = counts["captured"] + counts["missed"] + counts["hallucinated"]
    captured_pct = _pct(counts["captured"], total)
    missed_pct = _pct(counts["missed"], total)
    hallucinated_pct = _pct(counts["hallucinated"], total)

    now = datetime.now(UTC)
    iso_timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    iso_date = now.strftime("%Y-%m-%d")
    notes = body.notes or ""

    rollup = {
        "timestamp": iso_timestamp,
        "film_id": film_id,
        "report_id": body.report_id,
        "prompt_version": body.prompt_version,
        "total_claims": total,
        "captured": counts["captured"],
        "missed": counts["missed"],
        "hallucinated": counts["hallucinated"],
        "captured_pct": captured_pct,
        "missed_pct": missed_pct,
        "hallucinated_pct": hallucinated_pct,
        "notes": notes,
    }

    # File writes happen after DB read closes. Ledger writes are append-only
    # — no concurrent writes expected (one grader, one session at a time),
    # so plain append-mode is sufficient.
    try:
        EVAL_SCORES_ROOT.mkdir(parents=True, exist_ok=True)

        if not EVAL_SCORES_MD.exists():
            EVAL_SCORES_MD.write_text(EVAL_SCORES_MD_HEADER, encoding="utf-8")

        md_row = (
            f"| {iso_date} "
            f"| {film_id or ''} "
            f"| {body.report_id} "
            f"| {_md_escape(body.prompt_version)} "
            f"| {total} "
            f"| {counts['captured']} "
            f"| {counts['missed']} "
            f"| {counts['hallucinated']} "
            f"| {captured_pct}% "
            f"| {missed_pct}% "
            f"| {hallucinated_pct}% "
            f"| {_md_escape(notes)} |\n"
        )
        with EVAL_SCORES_MD.open("a", encoding="utf-8") as f:
            f.write(md_row)

        with EVAL_SCORES_JSONL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rollup) + "\n")
    except OSError as e:
        # Surface filesystem failures (permission, missing mount) with the
        # path so the network-tab error gives Tommy enough to fix it. The
        # corrections rows are already in the DB — eval ledger is derived.
        logger.error(
            "EVAL_SCORES write failed",
            extra={
                "report_id": body.report_id,
                "prompt_version": body.prompt_version,
                "path": str(EVAL_SCORES_ROOT),
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to write EVAL_SCORES at {EVAL_SCORES_ROOT}: {e}",
        ) from e

    # R12: flight-recorder snapshot. Runs after the EVAL_SCORES writes so a
    # snapshot failure can't block the ledger row (the rollup is the
    # longitudinal signal — the snapshot is the forensic backup). On
    # snapshot-only failures we surface the error in the response without
    # raising, so the frontend can show a soft warning.
    snapshot_path: str | None = None
    snapshot_error: str | None = None

    # ground_truth_ref: only set if the grader's selected slug passes the same
    # regex we apply to /admin/golden-set URLs. Anything else → null, per
    # spec ("better null than wrong").
    ground_truth_ref: str | None = None
    if body.film_slug and GOLDEN_SLUG_PATTERN.match(body.film_slug):
        ground_truth_ref = f"golden_set/{body.film_slug}/ground_truth.md"

    report_content = {section_type: content for section_type, content in section_rows}
    classifications = [
        {
            "section_type": r[0],
            "claim_status": r[1],
            "ai_claim": r[2],
            "correct_claim": r[3],
            "created_at": r[4].isoformat() if r[4] else None,
        }
        for r in classification_rows
    ]

    snapshot = {
        "snapshot_version": SNAPSHOT_SCHEMA_VERSION,
        "report_id": body.report_id,
        "film_id": film_id,
        "prompt_version": body.prompt_version,
        "graded_at": iso_timestamp,
        "session_started_at": body.session_started_at.astimezone(UTC).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "notes": notes,
        "rollup": {
            "total_claims": total,
            "captured": counts["captured"],
            "missed": counts["missed"],
            "hallucinated": counts["hallucinated"],
            "captured_pct": captured_pct,
            "missed_pct": missed_pct,
            "hallucinated_pct": hallucinated_pct,
        },
        "report_content": report_content,
        "ground_truth_ref": ground_truth_ref,
        "classifications": classifications,
    }

    # Filename: {film_id}_{prompt_version}_{ISO8601_compact}.json. Colons in
    # the timestamp are replaced with hyphens so the name is safe on Windows
    # / macOS as well as Linux. Falls back to "unknown" if film_id is null
    # (zero-classification session against a report with no films).
    compact_ts = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    safe_film_id = film_id or "unknown"
    safe_prompt_version = re.sub(r"[^A-Za-z0-9._-]", "_", body.prompt_version)
    snapshot_filename = f"{safe_film_id}_{safe_prompt_version}_{compact_ts}.json"
    snapshot_file = EVAL_SNAPSHOTS_DIR / snapshot_filename

    try:
        EVAL_SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        snapshot_file.write_text(
            json.dumps(snapshot, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        snapshot_path = f"eval_snapshots/{snapshot_filename}"
    except OSError as e:
        snapshot_error = str(e)
        logger.error(
            "Eval snapshot write failed",
            extra={
                "report_id": body.report_id,
                "prompt_version": body.prompt_version,
                "path": str(snapshot_file),
                "error": snapshot_error,
            },
        )

    logger.info(
        "Grading session logged to EVAL_SCORES",
        extra={
            "report_id": body.report_id,
            "prompt_version": body.prompt_version,
            "total_claims": total,
            "captured": counts["captured"],
            "missed": counts["missed"],
            "hallucinated": counts["hallucinated"],
            "snapshot_path": snapshot_path,
            "snapshot_error": snapshot_error,
        },
    )

    rollup["snapshot_path"] = snapshot_path
    rollup["snapshot_error"] = snapshot_error
    return rollup


# ---------------------------------------------------------------------------
# 4.4 — GET /admin/pattern-analysis
# ---------------------------------------------------------------------------


@router.get("/pattern-analysis")
async def pattern_analysis(
    prompt_version: str | None = Query(None),
    user: dict = Depends(require_admin),
):
    """Error rate by category and section type for a given prompt version.

    Returns aggregated stats showing where the AI is making mistakes,
    so Tommy knows which prompts to improve.
    """
    version_filter = ""
    params: list = []
    if prompt_version:
        version_filter = "WHERE prompt_version = %s"
        params.append(prompt_version)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Error rate by category
            cur.execute(
                f"SELECT category, "
                f"COUNT(*) as total, "
                f"SUM(CASE WHEN is_correct = false THEN 1 ELSE 0 END) as errors, "
                f"ROUND(100.0 * SUM(CASE WHEN is_correct = false THEN 1 ELSE 0 END) / "
                f"NULLIF(COUNT(*), 0), 1) as error_rate "
                f"FROM corrections {version_filter} "
                f"GROUP BY category ORDER BY error_rate DESC NULLS LAST",
                params,
            )
            by_category = [
                {
                    "category": r[0],
                    "total": r[1],
                    "errors": r[2],
                    "error_rate": float(r[3]) if r[3] else 0,
                }
                for r in cur.fetchall()
            ]

            # Error rate by section type
            cur.execute(
                f"SELECT section_type, "
                f"COUNT(*) as total, "
                f"SUM(CASE WHEN is_correct = false THEN 1 ELSE 0 END) as errors, "
                f"ROUND(100.0 * SUM(CASE WHEN is_correct = false THEN 1 ELSE 0 END) / "
                f"NULLIF(COUNT(*), 0), 1) as error_rate "
                f"FROM corrections {version_filter} "
                f"GROUP BY section_type ORDER BY error_rate DESC NULLS LAST",
                params,
            )
            by_section = [
                {
                    "section_type": r[0],
                    "total": r[1],
                    "errors": r[2],
                    "error_rate": float(r[3]) if r[3] else 0,
                }
                for r in cur.fetchall()
            ]

            # Overall stats
            cur.execute(
                f"SELECT COUNT(*), "
                f"SUM(CASE WHEN is_correct = false THEN 1 ELSE 0 END), "
                f"COUNT(DISTINCT prompt_version) "
                f"FROM corrections {version_filter}",
                params,
            )
            overall = cur.fetchone()

            # Available prompt versions
            cur.execute(
                "SELECT DISTINCT prompt_version FROM corrections ORDER BY prompt_version DESC"
            )
            versions = [r[0] for r in cur.fetchall()]

    finally:
        conn.close()

    return {
        "by_category": by_category,
        "by_section": by_section,
        "total_corrections": overall[0] or 0,
        "total_errors": overall[1] or 0,
        "prompt_versions_reviewed": overall[2] or 0,
        "available_versions": versions,
    }


# ---------------------------------------------------------------------------
# 4.5 — GET /admin/users
# ---------------------------------------------------------------------------


@router.get("/users")
async def list_users(user: dict = Depends(require_admin)):
    """List all coaches with report counts."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT u.id, u.email, u.is_admin, u.reports_used, "
                "u.report_credits, u.created_at, "
                "(SELECT COUNT(*) FROM reports r WHERE r.user_id = u.id "
                " AND r.deleted_at IS NULL) as report_count "
                "FROM users u WHERE u.deleted_at IS NULL "
                "ORDER BY u.created_at DESC"
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "id": str(r[0]),
            "email": r[1],
            "is_admin": r[2],
            "reports_used": r[3],
            "report_credits": r[4],
            "created_at": r[5].isoformat() if r[5] else None,
            "report_count": r[6],
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 4.6 — POST /admin/users/{id}/credits
# ---------------------------------------------------------------------------


@router.post("/users/{user_id}/credits")
async def grant_credits(
    user_id: str,
    body: CreditGrant,
    user: dict = Depends(require_admin),
):
    """Manually grant report credits to a coach."""
    if body.credits < 1:
        raise HTTPException(status_code=400, detail="Credits must be at least 1")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET report_credits = report_credits + %s, "
                "updated_at = now() WHERE id = %s AND deleted_at IS NULL "
                "RETURNING report_credits",
                (body.credits, user_id),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
    finally:
        conn.close()

    logger.info(
        "Credits granted",
        extra={
            "target_user_id": user_id,
            "credits_granted": body.credits,
            "new_balance": row[0],
            "admin_id": str(user["id"]),
        },
    )
    return {"user_id": user_id, "credits_granted": body.credits, "new_balance": row[0]}
