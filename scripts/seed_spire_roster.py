"""
Seed the Spire Institute Academy roster into Neon dev.

Mirrors scripts/seed_bbe_roster.py and scripts/seed_rebels_roster.py. Follows the
same idempotent DELETE + INSERT pattern. Roster sourced from the public Spire
Institute Academy V. Basketball roster page (screenshot, April 2026, 2025-26
season). Run once to seed, re-run to update.

Context: Films 01 / 02 are EYBL Peach Jam (17U club / AAU). Film 03 (this team)
is from the Nike EYBL Scholastic League — high school prep program play during
the 2025-26 academic season. Different roster, different context. Some players
overlap with summer-circuit teams (e.g. #32 Jaylan Mitchell is on both BBE film 01
and Spire film 03 — confirmed same player, two programs).

Requires:
  1. A Spire Institute Academy team row to exist in the `teams` table (create via
     /admin or a migration — don't hand-insert here). Set TEAM_ID below to that
     row's UUID before running.
  2. NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD in backend/.env.

Usage:
    python scripts/seed_spire_roster.py

Status: PENDING TEAM_ID. ROSTER is populated. Set TEAM_ID after creating the
team row in /admin, then run.
"""

import os
import sys

import psycopg2

# ==== FILL IN BEFORE RUNNING =================================================

# The Spire Institute Academy team_id from the `teams` table. Obtain by
# inserting the team row via /admin (or a migration) first, then paste the
# UUID here.
TEAM_ID: str | None = "e0a77555-7eec-47a9-b480-8feb399d743a"  # Spire Academy (created via /admin 2026-04-26)

USER_ID = "933c00c7-df54-43a4-ae2d-f36502347cce"  # Tommy / admin

# Source: Spire Institute Academy V. Basketball public roster (screenshot,
# April 2026, 2025-26 season). 12 players.
#
# Position mapping from roster sheet:
#   G → PG (default; #2 / #3 may split PG vs SG roles — confirm from film)
#   W → SF
#   F → PF
#   C → C
#
# Three players (#1, #12, #55) had blank position cells on the published roster.
# Defaulted by height — confirm and update after first watch:
#   #1 Aiden Dayco-Green (6'5" Jr) → SF
#   #12 Jalen Parker      (6'4" So) → PG  (shorter, likely guard)
#   #55 Nolan Nelson      (6'8" Jr) → PF
#
# Refine position, dominant_hand, and role from film observations.
ROSTER: list[dict] = [
    {"jersey": "0",  "name": "Tarris Bouie III",       "pos": "SF", "height": "6'5\"",  "grad_year": "2026", "class_yr": "Sr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "1",  "name": "Aiden Dayco-Green",      "pos": "SF", "height": "6'5\"",  "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "2",  "name": "King Gibson",            "pos": "PG", "height": "6'4\"",  "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "3",  "name": "Darrell Davis",          "pos": "PG", "height": "5'11\"", "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "4",  "name": "Aiden Derkack",          "pos": "SF", "height": "6'6\"",  "grad_year": "2026", "class_yr": "Sr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "5",  "name": "Alex Constanza",         "pos": "SF", "height": "6'9\"",  "grad_year": "2026", "class_yr": "Sr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "11", "name": "Charles Pur",            "pos": "C",  "height": "6'9\"",  "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "12", "name": "Jalen Parker",           "pos": "PG", "height": "6'4\"",  "grad_year": "2028", "class_yr": "So", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "14", "name": "Dorian Rinaldo-Komlan",  "pos": "PF", "height": "6'10\"", "grad_year": "2026", "class_yr": "Sr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "32", "name": "Jaylan Mitchell",        "pos": "PF", "height": "6'7\"",  "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "55", "name": "Nolan Nelson",           "pos": "PF", "height": "6'8\"",  "grad_year": "2027", "class_yr": "Jr", "hs": "Spire Institute Academy (OH)"},
    {"jersey": "93", "name": "Collin Ross",            "pos": "C",  "height": "6'10\"", "grad_year": "2026", "class_yr": "Sr", "hs": "Spire Institute Academy (OH)"},
]

# =============================================================================

DEFAULT_HAND = "right"
DEFAULT_ROLE = "role_player"


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def preflight() -> None:
    if not TEAM_ID:
        print("ERROR: TEAM_ID is not set. Insert the Spire Institute Academy team")
        print("       row via /admin (or a migration) first, then paste the UUID")
        print("       at the top of this script.")
        sys.exit(1)
    if not ROSTER:
        print("ERROR: ROSTER is empty. Populate with the confirmed Spire Institute")
        print("       roster (jersey, name, pos, height, grad_year, hs) before running.")
        sys.exit(1)
    for var in ("NEON_HOST", "NEON_DB", "NEON_USER", "NEON_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: {var} not set.")
            sys.exit(1)


def main():
    load_env()
    preflight()

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
                "SELECT name FROM teams WHERE id = %s AND deleted_at IS NULL;",
                (TEAM_ID,),
            )
            row = cur.fetchone()
            if not row:
                print(f"ERROR: team {TEAM_ID} not found or soft-deleted.")
                sys.exit(1)
            print(f"Target team: {row[0]} ({TEAM_ID})")

            cur.execute(
                "SELECT jersey_number, full_name FROM roster_players "
                "WHERE team_id = %s ORDER BY jersey_number;",
                (TEAM_ID,),
            )
            existing = cur.fetchall()
            print(f"Existing roster rows: {len(existing)}")
            for r in existing:
                print(f"  #{r[0]}: {r[1]}")

            cur.execute(
                "DELETE FROM roster_players WHERE team_id = %s;",
                (TEAM_ID,),
            )
            print(f"Deleted {cur.rowcount} existing rows.")

            insert_sql = """
                INSERT INTO roster_players
                    (user_id, team_id, jersey_number, full_name, position,
                     height, dominant_hand, role, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for p in ROSTER:
                notes = f"{p['class_yr']} | {p['grad_year']} | {p['hs']}"
                cur.execute(
                    insert_sql,
                    (
                        USER_ID,
                        TEAM_ID,
                        p["jersey"],
                        p["name"],
                        p["pos"],
                        p["height"],
                        DEFAULT_HAND,
                        DEFAULT_ROLE,
                        notes,
                    ),
                )
                print(f"  Inserted #{p['jersey']:>2} {p['name']:<24} {p['pos']} {p['height']}")

        conn.commit()
        print(f"\nSeeded {len(ROSTER)} players to Spire Institute Academy.")

        with conn.cursor() as cur:
            cur.execute(
                "SELECT jersey_number, full_name, position, height, dominant_hand, role "
                "FROM roster_players WHERE team_id = %s "
                "ORDER BY CAST(jersey_number AS integer);",
                (TEAM_ID,),
            )
            print("\nFinal roster in DB:")
            print("  #  | Name                     | Pos | Ht     | Hand  | Role")
            print("  ---|--------------------------|-----|--------|-------|------------")
            for r in cur.fetchall():
                print(f"  {r[0]:>2} | {r[1]:<24} | {r[2]:<3} | {r[3]:<6} | {r[4]:<5} | {r[5]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
