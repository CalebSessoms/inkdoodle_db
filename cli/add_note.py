# add_note.py — insert a note (optionally tied to work and/or chapter)
from db_conn import get_conn
import json

if __name__ == "__main__":
    user = input("User ID (e.g., 1): ").strip()
    if not user.isdigit():
        raise SystemExit("User ID must be a number.")
    user_id = int(user)

    work = input("Work ID (blank = none): ").strip()
    work_id = int(work) if work.isdigit() else None

    chapter = input("Chapter ID (blank = none): ").strip()
    chapter_id = int(chapter) if chapter.isdigit() else None

    title = input("Note title: ").strip()
    if not title:
        raise SystemExit("Note title is required.")

    body = input("Body (Markdown ok, blank = none): ").strip() or None

    tags = input('Tags (comma-separated, blank = none): ').strip()
    tags_json = json.dumps([t.strip() for t in tags.split(",") if t.strip()]) if tags else None

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO notes (user_id, work_id, chapter_id, title, body_md, tags_json) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (user_id, work_id, chapter_id, title, body, tags_json),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Created note id={new_id} (user {user_id}, work {work_id}, chapter {chapter_id}, title '{title}')")
        except Exception as e:
            conn.rollback()
            print("Failed to add note:", e)
        finally:
            cur.close()
