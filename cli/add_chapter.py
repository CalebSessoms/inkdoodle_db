# add_chapter.py — insert a chapter for a given work_id
from db_conn import get_conn

def next_chapter_number(conn, work_id: int) -> int:
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(number), 0) + 1 FROM chapters WHERE work_id = %s;", (work_id,))
    n = cur.fetchone()[0]
    cur.close()
    return n

if __name__ == "__main__":
    work = input("Work ID (e.g., 1 or 2): ").strip()
    if not work.isdigit():
        raise SystemExit("Work ID must be a number.")
    work_id = int(work)

    title = input("Chapter title: ").strip()
    if not title:
        raise SystemExit("Chapter title is required.")

    number_in = input("Chapter number (blank = next): ").strip()
    content = input("Content (optional, Markdown ok): ").strip()
    status  = input("Status [draft/final] (blank = draft): ").strip().lower() or "draft"
    if status not in {"draft", "final"}:
        raise SystemExit("Status must be 'draft' or 'final'.")

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            number = int(number_in) if number_in else next_chapter_number(conn, work_id)
            cur.execute(
                "INSERT INTO chapters (work_id, number, title, content_md, status) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (work_id, number, title, content or None, status),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Created chapter id={new_id} (work {work_id}, number {number}, title '{title}')")
        except Exception as e:
            conn.rollback()
            print("Failed to add chapter:", e)
        finally:
            cur.close()
