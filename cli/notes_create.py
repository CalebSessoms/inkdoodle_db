# cli/notes_create.py — create a new note (creator-scoped code auto via trigger)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def next_int_or_none(s: str):
    s = s.strip()
    return int(s) if s.isdigit() else None

def main():
    print("=== Create Note ===")
    project_id = input("Project ID: ").strip()
    creator_id = input("Creator ID: ").strip()
    number_raw = input("Note number (blank = auto/next): ").strip()
    title = input("Note title: ").strip()
    content = input("Content (optional): ").strip() or None
    tags_raw = input("Tags (comma-separated, blank = none): ").strip()
    category = input("Category (optional): ").strip() or None
    pinned_s = (input("Pinned? [y/N]: ").strip().lower() or "n")

    if not project_id or not creator_id or not title:
        print("Project ID, Creator ID, and Title are required.")
        return

    number = next_int_or_none(number_raw)
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] or None
    pinned = pinned_s in ("y", "yes", "true", "1")

    with get_conn() as conn:
        cur = conn.cursor()
        # If number is None, let DB accept NULL (no uniqueness break unless you added unique (project_id, number))
        cur.execute(
            """
            INSERT INTO notes (project_id, creator_id, number, title, content, tags, category, pinned)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, code;
            """,
            (project_id, creator_id, number, title, content, tags, category, pinned)
        )
        nid, ncode = cur.fetchone()
        conn.commit()
        cur.close()

    print(f"✅ Created note id={nid}, code={ncode} (project {project_id}, number {number}, title '{title}')")

if __name__ == "__main__":
    main()

