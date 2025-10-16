# users_create.py — create a new user (creator)
from db_conn import get_conn

def main():
    email = input("Email: ").strip()
    display = input("Display name: ").strip()
    # Placeholder hash (replace with real hashing later)
    pwd_hash = input("Temp password (stored as placeholder hash): ").strip() or "pbkdf2$demo$hash"

    if not email or not display:
        raise SystemExit("Email and display name are required.")

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (email, password_hash, display_name) VALUES (%s, %s, %s) RETURNING id;",
                (email, pwd_hash, display),
            )
            uid = cur.fetchone()[0]
            conn.commit()
            print(f"Created user id={uid} ({email})")
        except Exception as e:
            conn.rollback()
            print("Failed to create user:", e)
        finally:
            cur.close()

if __name__ == "__main__":
    main()
