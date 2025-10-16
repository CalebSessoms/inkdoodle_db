# add_ref.py — attach a reference (URL) to a note, or optionally to a work/chapter
from db_conn import get_conn

if __name__ == "__main__":
    # Primary association — recommend using note_id
    note = input("Note ID to attach to (e.g., 2): ").strip()
    note_id = int(note) if note.isdigit() else None

    # Optional associations (for flexibility)
    work = input("Work ID (blank = none): ").strip()
    work_id = int(work) if work.isdigit() else None

    chapter = input("Chapter ID (blank = none): ").strip()
    chapter_id = int(chapter) if chapter.isdigit() else None

    if not (note_id or work_id or chapter_id):
        raise SystemExit("You must provide at least one of: Note ID, Work ID, or Chapter ID.")

    label = input("Reference label (e.g., Inspiration link): ").strip()
    if not label:
        raise SystemExit("Label is required.")

    url = input("URL: ").strip()
    if not url:
        raise SystemExit("URL is required.")

    ref_type = (input("Type [article/image/video/other] (blank = other): ").strip().lower() or "other")

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO refs (work_id, chapter_id, note_id, label, url, ref_type) "
                "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                (work_id, chapter_id, note_id, label, url, ref_type),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Created ref id={new_id} (note={note_id}, work={work_id}, chapter={chapter_id})")
        except Exception as e:
            conn.rollback()
            print("Failed to add ref:", e)
        finally:
            cur.close()
