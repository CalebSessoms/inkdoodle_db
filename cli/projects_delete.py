# cli/projects_delete.py — delete a project after previewing dependent rows
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def resolve_project_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM projects WHERE code = %s;", (token,))
    r = cur.fetchone()
    return r[0] if r else None

def main():
    token = input("Project ID (number) or CODE: ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        pid = resolve_project_id(cur, token)
        if not pid:
            print(f"No project found for '{token}'")
            return

        # fetch a summary
        cur.execute("""
            SELECT p.id, p.code, p.title, c.display_name
            FROM projects p
            JOIN creators c ON c.id = p.creator_id
            WHERE p.id = %s
        """, (pid,))
        proj = cur.fetchone()
        if not proj:
            print(f"No project found with id={pid}")
            return

        # dependent counts (what will be removed by CASCADE)
        cur.execute("SELECT COUNT(*) FROM chapters WHERE project_id = %s", (pid,))
        ch_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM notes WHERE project_id = %s", (pid,))
        nt_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM refs WHERE project_id = %s", (pid,))
        rf_count = cur.fetchone()[0]

        print("\n== DELETE PREVIEW ==")
        print(f"Project: id={proj[0]} code={proj[1]} title='{proj[2]}' (creator: {proj[3]})")
        print(f"Will also delete: chapters={ch_count}, notes={nt_count}, refs={rf_count}")
        ans = input("Type DELETE to confirm: ").strip()
        if ans != "DELETE":
            print("Aborted.")
            return

        cur.execute("DELETE FROM projects WHERE id = %s", (pid,))
        conn.commit()
        print("✅ Project and dependents deleted.")
        cur.close()

if __name__ == "__main__":
    main()
