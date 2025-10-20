# cli/chapters_delete.py — delete a chapter by ID or CODE (asks for confirmation)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def resolve_chapter_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM chapters WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def main():
    token = input("Chapter (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        cid = resolve_chapter_id(cur, token)
        if not cid:
            print(f"No chapter found for '{token}'")
            return

        cur.execute("""
            SELECT ch.id, ch.code, ch.project_id, ch.creator_id, ch.number, ch.title, ch.status
            FROM chapters ch
            WHERE ch.id = %s
        """, (cid,))
        row = cur.fetchone()
        if not row:
            print(f"No chapter found with id={cid}")
            return

        print("\n== DELETE PREVIEW ==")
        print(f"id={row[0]} code={row[1]} project_id={row[2]} creator_id={row[3]}")
        print(f"number={row[4]} title='{row[5]}' status={row[6]}")
        print("(Chapters have no dependent rows; this will remove only this chapter.)")
        confirm = input("Type DELETE to confirm: ").strip()
        if confirm != "DELETE":
            print("Aborted.")
            return

        cur.execute("DELETE FROM chapters WHERE id = %s", (cid,))
        conn.commit()
        cur.close()
        print("✅ Chapter deleted.")

if __name__ == "__main__":
    main()
