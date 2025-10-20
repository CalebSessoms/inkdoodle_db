# cli/creators_list.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from inkdb.db import get_conn

if __name__ == "__main__":
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, display_name, created_at, is_active
            FROM creators
            ORDER BY id;
        """)
        rows = cur.fetchall()
        cur.close()

    print("\n== Creators ==")
    print("id | email | display_name | created_at | active")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
