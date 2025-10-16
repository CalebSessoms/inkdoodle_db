# list_works.py — prints users, works, chapters, notes, refs (first few rows)
import os, ssl
from urllib.parse import urlparse
from dotenv import load_dotenv
import pg8000

def get_conn():
    load_dotenv()  # loads DATABASE_URL from .env in this folder
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL missing from .env")
    u = urlparse(url)
    ssl_ctx = ssl.create_default_context()
    return pg8000.connect(
        user=u.username, password=u.password,
        host=u.hostname, port=u.port or 5432,
        database=(u.path or "").lstrip("/"),
        ssl_context=ssl_ctx
    )

def show(cur, title, sql):
    print(f"\n== {title} ==")
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    print(" | ".join(cols))
    for row in cur.fetchall():
        print(" | ".join(str(x) for x in row))

if __name__ == "__main__":
    with get_conn() as conn:
        cur = conn.cursor()
        show(cur, "Users",    "SELECT id, email, display_name FROM users ORDER BY id LIMIT 10;")
        show(cur, "Works",    "SELECT id, owner_user_id, title, slug FROM works ORDER BY id LIMIT 10;")
        show(cur, "Chapters", "SELECT id, work_id, number, title, status FROM chapters ORDER BY id LIMIT 10;")
        show(cur, "Notes",    "SELECT id, user_id, work_id, chapter_id, title FROM notes ORDER BY id LIMIT 10;")
        show(cur, "Refs",     "SELECT id, note_id, label, url, ref_type FROM refs ORDER BY id LIMIT 10;")
        cur.close()
