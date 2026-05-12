"""
One-time migration: reclassify EYBL Scholastic teams (Films 03/04/05) from
the generic `eybl` level to the new `eybl_scholastic` level.

Background: when these teams were created in /admin, only `eybl` existed as
a level option in the frontend. Now that we've added `eybl_scholastic`
(high-school prep program play, Films 03-05) alongside `eybl` (summer
17U/AAU circuit, Films 01-02), the prep-program teams need their level
updated.

Films 01-02 (BBE, Florida Rebels) stay as `eybl` — those are EYBL summer
circuit (Peach Jam) games.
Films 03-05 (Spire, La Lumiere, Montverde, Brewster) move to `eybl_scholastic`.

Idempotent — safe to run multiple times.

Usage:
    python scripts/update_team_levels.py
"""

import os
import sys

import psycopg2

PREP_TEAMS_TO_RECLASSIFY = [
    "Spire Academy",
    "La Lumiere",
    "Montverde Academy",
    "Brewster Academy",
]

NEW_LEVEL = "eybl_scholastic"


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    for var in ("NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: {var} not set.")
            sys.exit(1)

    conn = psycopg2.connect(
        host=os.environ["NEON_HOST"],
        database=os.environ["NEON_DB"],
        user=os.environ["NEON_USER"],
        password=os.environ["NEON_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
    )

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, level FROM teams "
                "WHERE name = ANY(%s) AND deleted_at IS NULL "
                "ORDER BY name;",
                (PREP_TEAMS_TO_RECLASSIFY,),
            )
            rows = cur.fetchall()

            print(f"Found {len(rows)} active prep-program teams:")
            for r in rows:
                marker = "(no change)" if r[2] == NEW_LEVEL else f"(was '{r[2]}')"
                print(f"  - {r[1]:<24} {marker}")
            print()

            cur.execute(
                "UPDATE teams SET level = %s, updated_at = now() "
                "WHERE name = ANY(%s) AND deleted_at IS NULL "
                "AND level != %s "
                "RETURNING id, name, level;",
                (NEW_LEVEL, PREP_TEAMS_TO_RECLASSIFY, NEW_LEVEL),
            )
            updated = cur.fetchall()
            conn.commit()

            print(f"Updated {len(updated)} teams to level='{NEW_LEVEL}':")
            for r in updated:
                print(f"  - {r[1]:<24} → {r[2]}")
            if not updated:
                print("  (all targeted teams were already at the new level — nothing to do)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
