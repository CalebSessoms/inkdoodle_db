# users_update.py — update a user's email and/or display_name
from db_conn import get_conn

if __name__ == "__main__":
    raw = input("User ID to update: ").strip()
    if not raw.isdigit():
        raise SystemExit("User ID must be a number.")
    user_id = int(raw)

    new_email = input("New email (blank = keep): ").strip() or None
    new_name  = input("New display name (blank = keep): ").strip() or None

    if not new_email and not new_name:
        raise SystemExit("Nothing to update.")

    sets, params = [], []
    if new_email:
        sets.append("email = %s")
        params.append(new_email)
    if new_name:
        sets.append("display_name = %s")
        params.append(new_name)

    params.append(user_id)

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(f"UPDATE users SET {', '.join(sets)} WHERE id = %s RETURNING id, email, display_name;", params)
            row = cur.fetchone()
            if not row:
                print(f"No user found with id={user_id}")
            else:
                conn.commit()
                print(f"Updated user: id={row[0]} email={row[1]} display_name={row[2]}")
        except Exception as e:
            conn.rollback()
            print("Failed to update user:", e)
        finally:
            cur.close()
