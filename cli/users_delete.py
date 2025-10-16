# users_delete.py — HARD DELETE a user (cascades to works/chapters/notes/refs)
from db_conn import get_conn

if __name__ == "__main__":
    raw = input("User ID to DELETE (hard delete): ").strip()
    if not raw.isdigit():
        raise SystemExit("User ID must be a number.")
    user_id = int(raw)

    confirm = input(f"Type DELETE-{user_id} to confirm: ").strip()
    if confirm != f"DELETE-{user_id}":
        raise SystemExit("Cancelled.")

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id = %s RETURNING %s;", (user_id, user_id))
            row = cur.fetchone()
            if not row:
                print(f"No user found with id={user_id}")
            else:
                conn.commit()
                print(f"User {user_id} deleted (cascaded).")
        except Exception as e:
            conn.rollback()
            print("Failed to delete user:", e)
        finally:
            cur.close()
