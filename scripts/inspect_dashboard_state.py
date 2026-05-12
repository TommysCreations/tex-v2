"""
Read-only diagnostic for "dashboard shows no teams" / "teams missing" issues.

Connects directly to Neon (using backend/.env credentials) and prints:
  1. Every users row (id, clerk_id, email, created_at)
  2. Every teams row regardless of user_id (id, name, level, user_id, created_at, deleted_at)
  3. Per-team roster_players counts
  4. Per-user team counts (helps identify which users.id owns the existing teams)

This bypasses the API entirely and queries Neon directly, so it tells you ground truth
about what's actually in the database.

Usage:
    python scripts/inspect_dashboard_state.py

After running, compare the printed `users.id` values to your seed scripts'
TEAM_ID values to figure out which user owns the existing teams. Then either
(a) sign in with the same Clerk account you used yesterday, or (b) re-assign
ownership, or (c) seed under your current user.

This script is read-only — it does not modify the DB.
"""

import os

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

    print(f"Connecting to: {os.environ.get('NEON_HOST')} / {os.environ.get('NEON_DB')}")
    print()

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
            # --- USERS ---
            cur.execute(
                "SELECT id, clerk_id, email, is_admin, deleted_at, created_at "
                "FROM users ORDER BY created_at;"
            )
            users = cur.fetchall()
            print(f"=== USERS ({len(users)} rows) ===")
            print(f"{'id':<38} {'clerk_id':<35} {'email':<30} {'admin':<5} {'deleted_at':<26}")
            print("-" * 140)
            for u in users:
                deleted = str(u[4])[:26] if u[4] else "(active)"
                email = (u[2] or "(no email)")[:30]
                print(f"{str(u[0]):<38} {(u[1] or '')[:35]:<35} {email:<30} {str(u[3]):<5} {deleted:<26}")
            print()

            # --- TEAMS (no user filter, no soft-delete filter) ---
            cur.execute(
                "SELECT t.id, t.name, t.level, t.user_id, t.created_at, t.deleted_at, "
                "u.email, u.clerk_id "
                "FROM teams t LEFT JOIN users u ON t.user_id = u.id "
                "ORDER BY t.created_at;"
            )
            teams = cur.fetchall()
            print(f"=== TEAMS ({len(teams)} rows, all states) ===")
            print(f"{'id':<38} {'name':<28} {'level':<12} {'owner email':<28} {'deleted':<10}")
            print("-" * 130)
            for t in teams:
                deleted = "SOFT-DEL" if t[5] else "active"
                owner_email = (t[6] or "(orphan)")[:28]
                print(f"{str(t[0]):<38} {t[1][:28]:<28} {(t[2] or '')[:12]:<12} {owner_email:<28} {deleted:<10}")
            print()

            # --- ROSTER COUNTS PER TEAM ---
            cur.execute(
                "SELECT t.id, t.name, COUNT(rp.id) AS player_count "
                "FROM teams t LEFT JOIN roster_players rp ON rp.team_id = t.id "
                "WHERE t.deleted_at IS NULL "
                "GROUP BY t.id, t.name ORDER BY t.created_at;"
            )
            roster_counts = cur.fetchall()
            print(f"=== ROSTER PLAYER COUNTS (active teams only) ===")
            print(f"{'team':<28} {'players':<10}")
            print("-" * 40)
            for r in roster_counts:
                print(f"{r[1][:28]:<28} {r[2]:<10}")
            print()

            # --- TEAMS PER USER ---
            cur.execute(
                "SELECT u.id, u.email, u.clerk_id, "
                "COUNT(CASE WHEN t.deleted_at IS NULL THEN 1 END) AS active_teams, "
                "COUNT(CASE WHEN t.deleted_at IS NOT NULL THEN 1 END) AS deleted_teams "
                "FROM users u LEFT JOIN teams t ON t.user_id = u.id "
                "WHERE u.deleted_at IS NULL "
                "GROUP BY u.id, u.email, u.clerk_id ORDER BY active_teams DESC;"
            )
            user_team_counts = cur.fetchall()
            print(f"=== TEAMS PER USER ===")
            print(f"{'user id':<38} {'email':<30} {'active':<8} {'deleted':<8}")
            print("-" * 90)
            for u in user_team_counts:
                email = (u[1] or "(no email)")[:30]
                print(f"{str(u[0]):<38} {email:<30} {u[3]:<8} {u[4]:<8}")
            print()

            # --- INTERPRETATION HINT ---
            active_owners = [u for u in user_team_counts if u[3] > 0]
            print(f"=== INTERPRETATION ===")
            if not active_owners:
                print("No user owns any active teams. Either all teams are soft-deleted, or")
                print("the teams table is empty in this DB.")
            elif len(active_owners) == 1:
                u = active_owners[0]
                print(f"All active teams are owned by user_id={u[0]}, email={u[1] or '(none)'},")
                print(f"clerk_id={u[2]}.")
                print()
                print("If your dashboard shows 'no teams', your current Clerk session is signed")
                print("in as a DIFFERENT user. Sign in with the email above to see them, or")
                print(f"re-assign team ownership: UPDATE teams SET user_id = '<your_new_user_id>'")
                print(f"WHERE user_id = '{u[0]}';")
            else:
                print(f"{len(active_owners)} different users own active teams:")
                for u in active_owners:
                    print(f"  - {u[1] or '(no email)'}: {u[3]} teams (user_id={u[0]})")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
