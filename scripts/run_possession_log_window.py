"""
DIAGNOSTIC one-off: run the Stage A possession-log pass on a SHORT VIDEO WINDOW.

This is a window-size diagnostic, NOT a fix and NOT a new feature. It answers a
single question: when the model only has to bind ~5 clean possessions instead of
a full ~25-minute chunk, does outcome/attribution accuracy improve?

The ONLY thing that differs from the normal pass (services/possession_log.py):
the video handed to Gemini is the FIRST N seconds of chunk 0, trimmed locally
with FFmpeg (stream copy, no re-encode), instead of the whole chunk. Everything
else is identical and reused directly from services/possession_log.py:
  * same prompt (possession_log.txt v1.2 — loaded via build_prompt, NOT edited),
  * same model + settings (provider.analyze_video -> Gemini 2.5 Pro),
  * same table + insert (possession_logs, _row_values / _INSERT_SQL),
  * its own fresh run_id so it never overwrites the full-chunk run.

Strictly read-only on every existing table except the append-only insert into
possession_logs. Never touches the report pipeline, films.status, film_chunks,
or the v1.2 prompt text. Timestamp handling is unchanged (still parked).

Usage:
    REDIS_URL=redis://localhost:6380/0 \\
    python scripts/run_possession_log_window.py <film_id> \\
        --opponent "Brewster" --scouted "Montverde" \\
        --chunk-index 0 --window-seconds 360
"""

import argparse
import json
import os
import subprocess
import sys
import uuid

_BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(_BACKEND))


def load_env() -> None:
    env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Short-window possession-log diagnostic.")
    parser.add_argument("film_id")
    parser.add_argument("--opponent", required=True)
    parser.add_argument("--scouted", default=None)
    parser.add_argument("--chunk-index", type=int, default=0)
    parser.add_argument("--start-seconds", type=int, default=0,
                        help="offset into the chunk video where the window begins (default 0). "
                             "Use this to skip pre-game footage and start at the tip.")
    parser.add_argument("--window-seconds", type=int, default=360,
                        help="length of the video window to chart (default 360 = 6 min)")
    args = parser.parse_args()
    film_id = args.film_id.strip()

    load_env()
    for var in ("NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD",
                "CLOUDFLARE_R2_BUCKET_FILMS", "GEMINI_API_KEY"):
        if not os.environ.get(var):
            print(f"ERROR: {var} environment variable is not set.")
            sys.exit(1)

    # Reuse the exact building blocks of the real pass — no reimplementation.
    from services.possession_log import build_prompt, parse_possessions, _row_values, _INSERT_SQL
    from services.ai.router import get_ai_provider
    from services.db import get_connection
    from services.gemini_files import delete_gemini_file, upload_to_gemini
    from services.r2 import download_from_r2
    from services.rate_limit import acquire_gemini_slot
    from services.roster_format import format_roster_for_prompt

    bucket = os.environ["CLOUDFLARE_R2_BUCKET_FILMS"]
    run_id = str(uuid.uuid4())
    ci = args.chunk_index
    tmp_files: list[str] = []
    ephemeral_uris: list[str] = []

    raw_path = f"/tmp/{film_id}_poss_window_chunk_{ci:03d}_raw.mp4"
    trimmed_path = (
        f"/tmp/{film_id}_poss_window_chunk_{ci:03d}_"
        f"{args.start_seconds}s_{args.window_seconds}s.mp4"
    )

    try:
        # 1. Read-only: scouted team, roster, and the chunk's R2 key.
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
                    "SELECT r2_chunk_key FROM film_chunks WHERE film_id = %s AND chunk_index = %s",
                    (film_id, ci),
                )
                chunk_row = cur.fetchone()
                if not chunk_row:
                    raise RuntimeError(f"Chunk {ci} not found for film {film_id}")
                r2_chunk_key = chunk_row[0]
        finally:
            conn.close()

        if not r2_chunk_key:
            raise RuntimeError(f"Chunk {ci} has no R2 key — video unrecoverable.")

        resolved_scouted = args.scouted or seeded_team_name
        if not resolved_scouted:
            raise RuntimeError("No scouted team name; pass --scouted.")

        roster_text = format_roster_for_prompt(team_id) if team_id else "(no roster data available)"
        prompt = build_prompt(resolved_scouted, args.opponent, roster_text)

        print(f"film_id:        {film_id}")
        print(f"run_id:         {run_id}")
        print(f"scouted:        {resolved_scouted}")
        print(f"opponent:       {args.opponent}")
        print(f"chunk_index:    {ci}")
        print(f"start_seconds:  {args.start_seconds}")
        print(f"window_seconds: {args.window_seconds}")
        print()

        # 2. Pull the durable R2 chunk and trim its FIRST window_seconds (stream
        #    copy — no re-encode, exact at the keyframe at t=0).
        tmp_files.append(raw_path)
        print(f"downloading R2 chunk {ci} -> {raw_path} ...")
        download_from_r2(bucket, r2_chunk_key, raw_path)
        full_dur = _ffprobe_duration(raw_path)
        print(f"full chunk {ci} duration: {full_dur:.1f}s ({full_dur/60:.1f} min)")

        tmp_files.append(trimmed_path)
        print(f"trimming {args.window_seconds}s starting at {args.start_seconds}s -> {trimmed_path} ...")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(args.start_seconds), "-i", raw_path,
             "-t", str(args.window_seconds), "-c", "copy", trimmed_path],
            capture_output=True, check=True,
        )
        trimmed_dur = _ffprobe_duration(trimmed_path)
        print(f"trimmed window duration: {trimmed_dur:.1f}s ({trimmed_dur/60:.1f} min)")
        print()

        # 3. Upload the trimmed window to a fresh, pass-owned Gemini file.
        print("uploading trimmed window to Gemini File API ...")
        result = upload_to_gemini(trimmed_path)
        gemini_uri = str(result["uri"])
        ephemeral_uris.append(gemini_uri)

        # 4. Same model / settings / prompt as the real pass.
        provider = get_ai_provider()
        acquire_gemini_slot("gemini-2.5-pro")
        print("charting window with Gemini 2.5 Pro ...")
        raw = provider.analyze_video(uris=[gemini_uri], prompt=prompt, section_type="possession_log")
        tokens_in = getattr(provider, "last_tokens_input", None)
        tokens_out = getattr(provider, "last_tokens_output", None)

        possessions = parse_possessions(raw)

        # 5. Append rows under the fresh run_id (chunk_index preserved).
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for pi, p in enumerate(possessions):
                    cur.execute(_INSERT_SQL, _row_values(film_id, run_id, ci, pi, p))
            conn.commit()
        finally:
            conn.close()

        print()
        print("=" * 70)
        print(f"INPUT TOKENS (verification):  {tokens_in}")
        print(f"OUTPUT TOKENS:                {tokens_out}")
        print(f"POSSESSIONS LOGGED:           {len(possessions)}")
        print(f"RUN_ID:                       {run_id}")
        print("=" * 70)
        print()
        print("--- LOGGED POSSESSIONS (full narrative rows) ---")
        print(json.dumps(possessions, indent=2))

    finally:
        for uri in ephemeral_uris:
            delete_gemini_file(uri)
        for path in tmp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                print(f"warning: failed to clean up {path}")


if __name__ == "__main__":
    main()
