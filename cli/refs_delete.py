# cli/refs_delete.py — delete a reference by ID or CODE (asks for confirmation)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def resolve_ref_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM refs WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def main():
    token = input("Ref (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        rid = resolve_ref_id(cur, token)
        if not rid:
            print(f"No ref found for '{token}'")
            return

        cur.execute("""
            SELECT r.id, r.code, r.project_id, r.creator_id, r.number, r.title, r.type
            FROM refs r
            WHERE r.id = %s
        """, (rid,))
        row = cur.fetchone()
        if not row:
            print(f"No ref found with id={rid}")
            return

        print("\n== DELETE PREVIEW ==")
        print(f"id={row[0]} code={row[1]} project_id={row[2]} creator_id={row[3]}")
        print(f"number={row[4]} title='{row[5]}' type={row[6]}")
        print("(Refs have no dependent rows; this will remove only this reference.)")
        confirm = input("Type DELETE to confirm: ").strip()
        if confirm != "DELETE":
            print("Aborted.")
            return

        cur.execute("DELETE FROM refs WHERE id = %s", (rid,))
        conn.commit()
        cur.close()
        print("✅ Ref deleted.")

if __name__ == "__main__":
    main()
