# users_deactivate.py — set is_active = FALSE for a user
from db_conn import get_conn

if __name__ == "__main__":
    raw = input("User ID to deactivate: ").strip()
    if not raw.isdigit():
        raise SystemExit("User ID must be a number.")
    user_id = int(raw)

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s RETURNING id, email;", (user_id,))
            row = cur.fetchone()
            if not row:
                print(f"No user found with id={user_id}")
            else:
                conn.commit()
                print(f"Deactivated user id={row[0]} ({row[1]})")
        except Exception as e:
            conn.rollback()
            print("Failed to deactivate user:", e)
        finally:
            cur.close()
