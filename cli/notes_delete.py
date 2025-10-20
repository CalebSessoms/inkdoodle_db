# cli/notes_delete.py — delete a note by ID or CODE (asks for confirmation)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def resolve_note_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM notes WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def main():
    token = input("Note (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        nid = resolve_note_id(cur, token)
        if not nid:
            print(f"No note found for '{token}'")
            return

        cur.execute("""
            SELECT n.id, n.code, n.project_id, n.creator_id, n.number, n.title, n.category, n.pinned
            FROM notes n
            WHERE n.id = %s
        """, (nid,))
        row = cur.fetchone()
        if not row:
            print(f"No note found with id={nid}")
            return

        print("\n== DELETE PREVIEW ==")
        print(f"id={row[0]} code={row[1]} project_id={row[2]} creator_id={row[3]}")
        print(f"number={row[4]} title='{row[5]}' category={row[6]} pinned={row[7]}")
        print("(Notes have no dependent rows; this will remove only this note.)")
        confirm = input("Type DELETE to confirm: ").strip()
        if confirm != "DELETE":
            print("Aborted.")
            return

        cur.execute("DELETE FROM notes WHERE id = %s", (nid,))
        conn.commit()
        cur.close()
        print("✅ Note deleted.")

if __name__ == "__main__":
    main()
