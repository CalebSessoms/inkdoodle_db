# cli/projects_create.py — create a new project for a creator, returning the public code
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # allow "inkdb" import when running from repo root

from inkdb.db import get_conn

def main():
    title = input("Project title: ").strip()
    if not title:
        raise SystemExit("Title is required.")

    creator_raw = input("Creator ID (e.g., 1): ").strip()
    if not creator_raw.isdigit():
        raise SystemExit("Creator ID must be a number.")
    creator_id = int(creator_raw)

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            # Trigger in DB will auto-generate projects.code like PRJ-0001-000001
            cur.execute(
                "INSERT INTO projects (title, creator_id) VALUES (%s, %s) RETURNING id, code;",
                (title, creator_id),
            )
            result = cur.fetchone()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()

    pid, code = result
    print(f"✅ Created project id={pid}, code={code}, title='{title}', (creator {creator_id})")

if __name__ == "__main__":
    main()
