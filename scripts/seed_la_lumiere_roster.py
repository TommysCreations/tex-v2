"""
Seed the La Lumiere School roster into Neon dev.

Mirrors scripts/seed_spire_roster.py and scripts/seed_montverde_roster.py. Follows
the same idempotent DELETE + INSERT pattern. Roster sourced from the public
La Lumiere Boys' National V. Basketball roster page (screenshot, April 2026,
2025-26 season — 13 players, full pos / ht / class data). Run once to seed,
re-run to update.

Context: Films 03 / 04 / 05 are all from the Nike EYBL Scholastic League — high
school prep program play during the 2025-26 academic season. La Lumiere is the
SCOUTED team in Film 05 (vs Oak Hill Academy) and was the OPPONENT in Film 03
(Spire vs La Lumiere). The same 13 players apply to both films. Seeding them
here makes them available to Film 05 as the scouted team.

Cross-film roster sanity check vs Film 03:
    Film 03's metadata listed 12 La Lumiere players (no #15 Cruz Mactavish). The
    most current published page (April 2026) shows 13 players — this seeder uses
    the 13-player version. Film 03's reference roster has been updated retroactively
    so all golden-set documents agree.

Requires:
  1. A La Lumiere School team row to exist in the `teams` table (create via
     /admin or a migration — don't hand-insert here). Set TEAM_ID below to that
     row's UUID before running.
  2. NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD in backend/.env.

Usage:
    python scripts/seed_la_lumiere_roster.py

Status: PENDING TEAM_ID. ROSTER is populated. Set TEAM_ID after creating the
team row in /admin, then run.
"""

import os
import sys

import psycopg2

# ==== FILL IN BEFORE RUNNING =================================================

# The La Lumiere School team_id from the `teams` table. Obtain by inserting the
# team row via /admin (or a migration) first, then paste the UUID here.
TEAM_ID: str | None = "84c9251e-6516-42af-bd67-a83513a8d0c5"  # La Lumiere (created via /admin)

USER_ID = "933c00c7-df54-43a4-ae2d-f36502347cce"  # Tommy / admin

# Source: La Lumiere School Boys' National V. Basketball public roster
# (screenshot, April 2026, 2025-26 season). 13 players, full pos / ht / class.
#
# Position mapping from roster sheet:
#   G → PG (default)
#   F → PF
#   C → C
#
# Tall guards flagged for review — the roster sheet doesn't distinguish PG / SG /
# SF for guards. Confirm dominant role from film:
#   #3 Jacob Webber   (6'6" Sr G) — could be SG / SF rather than primary handler
#   #15 Cruz Mactavish (6'5" Jr G) — same
#
# Class-year → grad-year mapping (2025-26 season):
#   Fr → 2029
#   So → 2028
#   Jr → 2027
#   Sr → 2026
#
# Refine position, dominant_hand, and role from film observations.
ROSTER: list[dict] = [
    {"jersey": "1",  "name": "Peyton Kemp",        "pos": "PG", "height": "6'2\"", "grad_year": "2027", "class_yr": "Jr", "hs": "La Lumiere School (IN)"},
    {"jersey": "2",  "name": "Devin Cleveland",    "pos": "PG", "height": "6'3\"", "grad_year": "2027", "class_yr": "Jr", "hs": "La Lumiere School (IN)"},
    {"jersey": "3",  "name": "Jacob Webber",       "pos": "PG", "height": "6'6\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "5",  "name": "Ben Levy",           "pos": "PG", "height": "6'3\"", "grad_year": "2027", "class_yr": "Jr", "hs": "La Lumiere School (IN)"},
    {"jersey": "10", "name": "Jonathan Sanderson", "pos": "PG", "height": "6'3\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "11", "name": "Gabe Weis",          "pos": "PF", "height": "6'7\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "15", "name": "Cruz Mactavish",     "pos": "PG", "height": "6'5\"", "grad_year": "2027", "class_yr": "Jr", "hs": "La Lumiere School (IN)"},
    {"jersey": "20", "name": "Ferlandes Wright",   "pos": "PF", "height": "6'8\"", "grad_year": "2027", "class_yr": "Jr", "hs": "La Lumiere School (IN)"},
    {"jersey": "21", "name": "Rivers Knight",      "pos": "PF", "height": "6'9\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "22", "name": "Will Chang",         "pos": "PG", "height": "6'2\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "24", "name": "Cuba Smith",         "pos": "PG", "height": "6'3\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
    {"jersey": "33", "name": "Charlie Yalden",     "pos": "C",  "height": "6'8\"", "grad_year": "2029", "class_yr": "Fr", "hs": "La Lumiere School (IN)"},
    {"jersey": "44", "name": "Gan Solongo",        "pos": "C",  "height": "7'0\"", "grad_year": "2026", "class_yr": "Sr", "hs": "La Lumiere School (IN)"},
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
        print("ERROR: TEAM_ID is not set. Insert the La Lumiere School team row")
        print("       via /admin (or a migration) first, then paste the UUID at")
        print("       the top of this script.")
        sys.exit(1)
    if not ROSTER:
        print("ERROR: ROSTER is empty. Populate with the confirmed La Lumiere")
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
        print(f"\nSeeded {len(ROSTER)} players to La Lumiere School.")

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
