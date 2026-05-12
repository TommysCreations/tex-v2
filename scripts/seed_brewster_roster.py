"""
Seed the Brewster Academy roster into Neon dev.

Mirrors the other golden-set seeders. Follows the same idempotent DELETE + INSERT
pattern. Roster sourced from the public Brewster Academy "Boys' National" V.
Basketball roster page (screenshot, April 2026, 2025-26 season). 11 players.

Context: Brewster is the OPPONENT in Film 04 (Montverde vs Brewster, EYBL
Scholastic). The film's `metadata.md` originally noted that opponent rosters
should not be seeded into `roster_players`. Tommy chose to create Brewster as
its own team in the dashboard anyway, so we seed the published roster here so
the dashboard shows full coverage.

Caveat: Brewster's seeded roster is not used by any film's ground_truth.md
(Brewster is not a scouted team). It exists only so the dashboard team card
shows a non-zero player count for visual consistency.

Requires:
  1. A Brewster Academy team row to exist in the `teams` table (already created
     via /admin — see TEAM_ID below).
  2. NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD in backend/.env.

Usage:
    python scripts/seed_brewster_roster.py

Status: READY. TEAM_ID and ROSTER populated.
"""

import os
import sys

import psycopg2

# ==== FILL IN BEFORE RUNNING =================================================

TEAM_ID: str | None = "cdd5dc8a-1dfb-43da-beb9-bcff70094b65"  # Brewster Academy

USER_ID = "933c00c7-df54-43a4-ae2d-f36502347cce"  # Tommy / admin

# Source: Brewster Academy Boys' National V. Basketball public roster
# (screenshot, April 2026, 2025-26 season). 11 players.
#
# Position mapping (same convention as Films 01-05 seeders):
#   PG → PG
#   G  → PG (default for guards; flag tall guards #1, #5, #10)
#   F  → PF (default; flag #32 6'11" who is likely a true 5)
#
# Class-year → grad-year (2025-26):
#   Fr → 2029, So → 2028, Jr → 2027, Sr → 2026
#
# Refine position, dominant_hand, and role from film observations during Film 04 watch.
ROSTER: list[dict] = [
    {"jersey": "0",  "name": "Antonio Pemberton", "pos": "PG", "height": "6'1\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Methuen, MA"},
    {"jersey": "1",  "name": "Darien Moore",      "pos": "PG", "height": "6'2\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Hudson, NY (Seton Hall commit)"},
    {"jersey": "2",  "name": "Michai White",      "pos": "PG", "height": "6'1\"",  "grad_year": "2028", "class_yr": "So", "hometown": "Hackensack, NJ"},
    {"jersey": "3",  "name": "Reece Ayala",       "pos": "PG", "height": "6'4\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Lawrence, MA"},
    {"jersey": "5",  "name": "Markus Kerr",       "pos": "PG", "height": "6'6\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Charlotte, NC"},
    {"jersey": "10", "name": "Kevin Wheatley",    "pos": "PG", "height": "6'6\"",  "grad_year": "2028", "class_yr": "So", "hometown": "Rahway, NJ"},
    {"jersey": "13", "name": "Kaiden Francis",    "pos": "PF", "height": "6'7\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Brooklyn, NY"},
    {"jersey": "21", "name": "Tayden Langdon",    "pos": "PG", "height": "6'2\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Birmingham, MI"},
    {"jersey": "25", "name": "Brayden Jones",     "pos": "PF", "height": "6'8\"",  "grad_year": "2026", "class_yr": "Sr", "hometown": "Wethersfield, CT"},
    {"jersey": "30", "name": "Mark Burns",        "pos": "PF", "height": "6'9\"",  "grad_year": "2027", "class_yr": "Jr", "hometown": "Belfast, Ireland"},
    {"jersey": "32", "name": "Eric Jacobsen",     "pos": "C",  "height": "6'11\"", "grad_year": "2026", "class_yr": "Sr", "hometown": "Colorado Springs, CO"},
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
        print("ERROR: TEAM_ID is not set.")
        sys.exit(1)
    if not ROSTER:
        print("ERROR: ROSTER is empty.")
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
        print(f"\nSeeded {len(ROSTER)} players to Brewster Academy.")

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
