"""
Manual one-off: run the Stage A possession-log pass over one film.

This is a STANDALONE perception/truth-layer pass. It reads the film's chunk
videos read-only and writes append-only rows to possession_logs. It does NOT
touch the report pipeline: no films.status changes, no run_chunk_synthesis or
generate_report interaction, no advisory lock.

Usage:
    python scripts/run_possession_log.py <film_id>

Film 01 (Brad Beal Elite vs Team Durant):
    python scripts/run_possession_log.py 6d28b154-237b-4900-8861-4bbddf56d89c

Requires NEON_*, CLOUDFLARE_R2_*, GEMINI_API_KEY, REDIS_URL in backend/.env.
Exits non-zero if any chunk failed.
"""

import os
import sys

# Make backend/ importable so `services.*` resolves.
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


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_possession_log.py <film_id>")
        sys.exit(2)
    film_id = sys.argv[1].strip()

    load_env()
    for var in (
        "NEON_HOST",
        "NEON_DB",
        "NEON_USER",
        "NEON_PASSWORD",
        "CLOUDFLARE_R2_BUCKET_FILMS",
    ):
        if not os.environ.get(var):
            print(f"ERROR: {var} environment variable is not set.")
            sys.exit(1)

    # Imported after sys.path + env are set.
    from services.possession_log import run_possession_log

    print(f"Running possession-log pass on film {film_id} ...")
    summary = run_possession_log(film_id)

    print()
    print(f"run_id:            {summary['run_id']}")
    print(f"team_id:           {summary['team_id']}")
    print(f"total possessions: {summary['total_possessions']}")
    print("per-chunk:")
    for c in summary["chunks"]:
        print(
            f"  chunk {c['chunk_index']}: {c['possessions']} possessions  [{c['status']}]"
        )

    if summary["failed_chunks"]:
        print(f"\nFAILED chunks: {summary['failed_chunks']}")
        sys.exit(1)
    print("\nDone. Rows appended to possession_logs.")


if __name__ == "__main__":
    main()
