# cli/chapters_list.py — list chapters (optionally filter by project)
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
                SELECT ch.id, ch.code, ch.project_id, ch.creator_id, ch.number,
                       ch.title, ch.status, ch.created_at
                FROM chapters ch
                WHERE ch.project_id = %s
                ORDER BY ch.project_id, ch.number;
            """, (by_project,))
        else:
            cur.execute("""
                SELECT ch.id, ch.code, ch.project_id, ch.creator_id, ch.number,
                       ch.title, ch.status, ch.created_at
                FROM chapters ch
                ORDER BY ch.project_id, ch.number;
            """)
        rows = cur.fetchall()
        cur.close()

    print("\n== Chapters ==")
    print("id | code | project_id | creator_id | number | title | status | created_at")
    for r in rows:
        print(" | ".join(str(x) for x in r))

if __name__ == "__main__":
    main()
