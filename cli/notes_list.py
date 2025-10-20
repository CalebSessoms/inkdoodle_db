# cli/notes_list.py — list notes (optionally filter by project)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def main():
    filt = input("Filter by Project ID (blank = all): ").strip()
    by_project = int(filt) if filt.isdigit() else None

    with get_conn() as conn:
        cur = conn.cursor()
        if by_project:
            cur.execute("""
                SELECT n.id, n.code, n.project_id, n.creator_id, n.number,
                       n.title, n.category, n.pinned, n.created_at
                FROM notes n
                WHERE n.project_id = %s
                ORDER BY n.project_id, n.number;
            """, (by_project,))
        else:
            cur.execute("""
                SELECT n.id, n.code, n.project_id, n.creator_id, n.number,
                       n.title, n.category, n.pinned, n.created_at
                FROM notes n
                ORDER BY n.project_id, n.number;
            """)
        rows = cur.fetchall()
        cur.close()

    print("\n== Notes ==")
    print("id | code | project_id | creator_id | number | title | category | pinned | created_at")
    for r in rows:
        print(" | ".join(str(x) for x in r))

if __name__ == "__main__":
    main()
