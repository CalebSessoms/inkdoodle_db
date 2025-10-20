# cli/chapters_create.py — create a new chapter
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # allow inkdb import
from inkdb.db import get_conn

def main():
    print("=== Create Chapter ===")
    project_id = input("Project ID: ").strip()
    creator_id = input("Creator ID: ").strip()
    number = input("Chapter number (optional): ").strip() or None
    title = input("Chapter title: ").strip()
    content = input("Content (optional): ").strip() or None
    status = input("Status [draft/final] (blank = draft): ").strip() or "draft"
    summary = input("Summary (optional): ").strip() or None
    tags_raw = input("Tags (comma-separated, blank = none): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] or None

    if not title:
        print("Title is required.")
        return
    if not project_id or not creator_id:
        print("Project ID and Creator ID are required.")
        return

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chapters (project_id, creator_id, number, title, content, status, summary, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, code;
            """,
            (project_id, creator_id, number, title, content, status, summary, tags)
        )
        cid, ccode = cur.fetchone()
        conn.commit()
        cur.close()

    print(f"✅ Created chapter id={cid}, code={ccode} (project {project_id}, number {number}, title '{title}')")

if __name__ == "__main__":
    main()
