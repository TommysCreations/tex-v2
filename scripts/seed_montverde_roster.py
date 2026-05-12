"""
Seed the Montverde Academy roster into Neon dev.

Mirrors scripts/seed_bbe_roster.py / seed_rebels_roster.py / seed_spire_roster.py.
Follows the same idempotent DELETE + INSERT pattern. Roster sourced from the
public Montverde Academy V. Basketball roster page (screenshot, April 2026,
2025-26 season). Run once to seed, re-run to update.

Context: Films 01 / 02 are EYBL Peach Jam (17U club / AAU). Films 03 (Spire)
and 04 (this team — Montverde) are from the Nike EYBL Scholastic League — high
school prep program play during the 2025-26 academic season. Same league as
Spire, four 8-min quarters confirmed.

Requires:
  1. A Montverde Academy team row to exist in the `teams` table (create via
     /admin or a migration — don't hand-insert here). Set TEAM_ID below to that
     row's UUID before running.
  2. NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD in backend/.env.

Usage:
    python scripts/seed_montverde_roster.py

Status: PENDING TEAM_ID. ROSTER is populated. Set TEAM_ID after creating the
team row in /admin, then run.
"""

import os
import sys

import psycopg2

# ==== FILL IN BEFORE RUNNING =================================================

# The Montverde Academy team_id from the `teams` table. Obtain by inserting
# the team row via /admin (or a migration) first, then paste the UUID here.
TEAM_ID: str | None = "177776fa-8136-497a-bbc2-d83ac1c11027"  # Montverde Academy (created via /admin)

USER_ID = "933c00c7-df54-43a4-ae2d-f36502347cce"  # Tommy / admin

# Source: Montverde Academy V. Basketball public roster (screenshot, April 2026,
# 2025-26 season). 11 players.
#
# Position mapping from roster sheet (matches Films 01-03 convention):
#   G   → PG   (default; flag tall guards like #12 Ndour 6'7" and #33 Hodge 6'6")
#   F   → PF   (default; flag #5 Cosby 6'10" who may be a true 5)
#   F/C → C    (treat as a 5 unless film proves otherwise)
#   C   → C    (none on this roster)
#
# Refine position, dominant_hand, and role from film observations.
ROSTER: list[dict] = [
    {"jersey": "1",  "name": "Joe Philon III",       "pos": "PF", "height": "6'8\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Tampa, FL"},
    {"jersey": "2",  "name": "Dhani Miller",         "pos": "PG", "height": "6'3\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Roselle, NJ"},
    {"jersey": "3",  "name": "Javion Tyndale",       "pos": "PG", "height": "5'9\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Mississauga, ON"},
    {"jersey": "5",  "name": "Lincoln Cosby",        "pos": "PF", "height": "6'10\"", "grad_year": "2027", "class_yr": "Jr", "hometown": "Cincinnati, OH"},
    {"jersey": "10", "name": "Nikos Koulisianis",    "pos": "PF", "height": "6'9\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Brno, Czech Republic"},
    {"jersey": "11", "name": "Oneal Delancy",        "pos": "PG", "height": "6'3\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "St Petersburg, FL"},
    {"jersey": "12", "name": "Sebastien Ndour",      "pos": "PG", "height": "6'7\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Mbour, Senegal"},
    {"jersey": "25", "name": "Trace Lopez",          "pos": "C",  "height": "6'9\"",  "grad_year": "2028", "class_yr": "So", "hometown": "Phoenix, AZ"},
    {"jersey": "32", "name": "Malachi Booker",       "pos": "PF", "height": "6'7\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Houston, TX"},
    {"jersey": "33", "name": "Jayden Hodge",         "pos": "PG", "height": "6'6\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Limburg, Belgium"},
    {"jersey": "42", "name": "Derek Daniels",        "pos": "C",  "height": "6'8\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Washington, DC"},
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
        print("ERROR: TEAM_ID is not set. Insert the Montverde Academy team")
        print("       row via /admin (or a migration) first, then paste the UUID")
        print("       at the top of this script.")
        sys.exit(1)
    if not ROSTER:
        print("ERROR: ROSTER is empty. Populate with the confirmed Montverde Academy")
        print("       roster (jersey, name, pos, height, grad_year, hometown) before running.")
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
                notes = f"{p['class_yr']} | {p['grad_year']} | {p['hometown']}"
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
        print(f"\nSeeded {len(ROSTER)} players to Montverde Academy.")

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
