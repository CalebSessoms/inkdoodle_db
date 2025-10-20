# cli/refs_list.py — list references (optionally filter by project)
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
                SELECT r.id, r.code, r.project_id, r.creator_id, r.number,
                       r.title, r.type, r.created_at
                FROM refs r
                WHERE r.project_id = %s
                ORDER BY r.project_id, r.number;
            """, (by_project,))
        else:
            cur.execute("""
                SELECT r.id, r.code, r.project_id, r.creator_id, r.number,
                       r.title, r.type, r.created_at
                FROM refs r
                ORDER BY r.project_id, r.number;
            """)
        rows = cur.fetchall()
        cur.close()

    print("\n== Refs ==")
    print("id | code | project_id | creator_id | number | title | type | created_at")
    for r in rows:
        print(" | ".join(str(x) for x in r))

if __name__ == "__main__":
    main()
