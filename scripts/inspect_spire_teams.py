"""
Read-only inspection script — find duplicate Spire Institute Academy team rows
in Neon dev so we can pick which one to keep.

Lists every team row whose name matches '%spire%' (case-insensitive), along with
the count of related rows in roster_players, films, and reports. Output is
read-only — this script never modifies the database.

Usage:
    python scripts/inspect_spire_teams.py
"""

import os
import sys

import psycopg2


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
                """
                SELECT id, name, user_id, created_at, deleted_at
                FROM teams
                WHERE name ILIKE %s
                ORDER BY created_at;
                """,
                ("%spire%",),
            )
            rows = cur.fetchall()

            if not rows:
                print("No teams matching '%spire%' found.")
                return

            print(f"Found {len(rows)} team row(s) matching 'spire':\n")
            for i, (team_id, name, user_id, created_at, deleted_at) in enumerate(rows, start=1):
                cur.execute(
                    "SELECT COUNT(*) FROM roster_players WHERE team_id = %s;",
                    (team_id,),
                )
                player_count = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM films WHERE team_id = %s;",
                    (team_id,),
                )
                film_count = cur.fetchone()[0]

                print(f"  [{i}] team_id      : {team_id}")
                print(f"      name         : {name}")
                print(f"      user_id      : {user_id}")
                print(f"      created_at   : {created_at}")
                print(f"      deleted_at   : {deleted_at}")
                print(f"      players      : {player_count}")
                print(f"      films        : {film_count}")
                print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
