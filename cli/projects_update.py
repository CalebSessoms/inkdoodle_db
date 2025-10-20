# cli/projects_update.py — update a project's title (bumps updated_at via trigger)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def main():
    proj = input("Project ID (number) or CODE (e.g., PRJ-0001-000001): ").strip()
    new_title = input("New title: ").strip()
    if not new_title:
        raise SystemExit("Title is required.")

    with get_conn() as conn:
        cur = conn.cursor()
        # resolve project id
        if proj.isdigit():
            project_id = int(proj)
        else:
            cur.execute("SELECT id FROM projects WHERE code = %s;", (proj,))
            row = cur.fetchone()
            if not row:
                print(f"No project found for code {proj}")
                return
            project_id = row[0]

        cur.execute("""
            UPDATE projects
               SET title = %s
             WHERE id = %s
         RETURNING id, code, title, updated_at;
        """, (new_title, project_id))
        row = cur.fetchone()
        if not row:
            print(f"No project found with id={project_id}")
        else:
            conn.commit()
            print(f"✅ Updated project id={row[0]} code={row[1]} title='{row[2]}' (updated_at {row[3]})")
        cur.close()

if __name__ == "__main__":
    main()
