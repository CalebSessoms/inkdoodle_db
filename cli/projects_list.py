# cli/projects_list.py — list projects
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

if __name__ == "__main__":
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.code, p.title, p.creator_id, p.created_at, p.updated_at,
                c.display_name AS creator_name
            FROM projects p
            JOIN creators c ON c.id = p.creator_id
            ORDER BY p.id;
            """)
        rows = cur.fetchall()
        cur.close()

    print("\n== Projects ==")
    print("id | code | title | creator_id | creator_name | created_at | updated_at")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[6]} | {r[4]} | {r[5]}")