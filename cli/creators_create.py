# cli/creators_create.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from inkdb.db import get_conn

if __name__ == "__main__":
    email = input("Creator email: ").strip()
    display_name = input("Display name: ").strip()
    password_hash = input("Password hash (temporary placeholder): ").strip() or "placeholder_hash"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO creators (email, password_hash, display_name)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (email, password_hash, display_name)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        print(f"✅ Created creator id={new_id}, name='{display_name}'")
