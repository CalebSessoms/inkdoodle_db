# create_work.py — insert a new Work for a given owner_user_id
from db_conn import get_conn
import re

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or 'untitled'

if __name__ == "__main__":
    title = input("Work title: ").strip()
    summary = input("Summary (optional): ").strip()
    owner = input("Owner user_id (e.g., 1): ").strip()

    if not title:
        raise SystemExit("Title is required.")
    if not owner.isdigit():
        raise SystemExit("Owner user_id must be a number.")
    owner_id = int(owner)

    slug = slugify(title)

    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO works (owner_user_id, title, slug, summary) VALUES (%s, %s, %s, %s) RETURNING id;",
                (owner_id, title, slug, summary or None),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Created work id={new_id}, title='{title}', slug='{slug}'")
        except Exception as e:
            conn.rollback()
            print("Failed to create work:", e)
        finally:
            cur.close()
