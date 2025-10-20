# cli/refs_create.py — create a new reference (creator-scoped code auto via trigger)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def next_int_or_none(s: str):
    s = s.strip()
    return int(s) if s.isdigit() else None

def main():
    print("=== Create Reference ===")
    project_id = input("Project ID: ").strip()
    creator_id = input("Creator ID: ").strip()
    number_raw = input("Ref number (blank = auto/next): ").strip()
    title = input("Ref title: ").strip()
    tags_raw = input("Tags (comma-separated, blank = none): ").strip()
    rtype = input("Type [article/image/video/book/other] (optional): ").strip() or None
    summary = input("Summary (optional): ").strip() or None
    link = input("Link (optional): ").strip() or None
    content = input("Content (optional): ").strip() or None

    if not project_id or not creator_id or not title:
        print("Project ID, Creator ID, and Title are required.")
        return

    number = next_int_or_none(number_raw)
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] or None

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO refs (project_id, creator_id, number, title, tags, type, summary, link, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, code;
            """,
            (project_id, creator_id, number, title, tags, rtype, summary, link, content)
        )
        rid, rcode = cur.fetchone()
        conn.commit()
        cur.close()

    print(f"✅ Created ref id={rid}, code={rcode} (project {project_id}, number {number}, title '{title}')")

if __name__ == "__main__":
    main()
