# cli/notes_update.py — update note fields by ID or CODE
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

def resolve_note_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM notes WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def prompt(current, label, allow_empty_keep=True):
    shown = current if current is not None else ""
    val = input(f"{label} [{shown}] (blank = keep): ").strip()
    if val == "" and allow_empty_keep:
        return None, False  # keep
    return val, True

def main():
    ident = input("Note (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        nid = resolve_note_id(cur, ident)
        if not nid:
            print(f"No note found for '{ident}'")
            return

        cur.execute("""
            SELECT id, code, project_id, creator_id, number, title, content, tags, category, pinned
            FROM notes
            WHERE id = %s
        """, (nid,))
        row = cur.fetchone()
        if not row:
            print(f"No note found for id={nid}")
            return

        (id_, code, project_id, creator_id, number, title, content, tags, category, pinned) = row
        print("\n== Current Note ==")
        print(f"id={id_} code={code} project_id={project_id} creator_id={creator_id}")
        print(f"number={number} title={title}")
        print(f"category={category} pinned={pinned}")
        print(f"tags={tags}")
        print("(content not shown)")

        # prompts (blank = keep)
        new_title, ch_title = prompt(title,   "New title")
        new_number_str, ch_number = prompt(number, "New number")
        new_category, ch_category = prompt(category, "New category")
        print("Pinned: enter y/yes/true to set True, n/no/false to set False, blank = keep")
        pin_in = input("Pinned: ").strip().lower()
        ch_pinned = False
        new_pinned = None
        if pin_in in ("y", "yes", "true", "1"):
            ch_pinned = True
            new_pinned = True
        elif pin_in in ("n", "no", "false", "0"):
            ch_pinned = True
            new_pinned = False

        print("Tags: enter comma-separated to replace, '-' to clear, or blank to keep")
        new_tags_in = input("New tags: ").strip()
        ch_tags = False
        new_tags = None
        if new_tags_in == "-":
            ch_tags = True
            new_tags = None
        elif new_tags_in != "":
            ch_tags = True
            new_tags = [t.strip() for t in new_tags_in.split(",") if t.strip()] or None

        new_content, ch_content = prompt("(hidden)", "New content (full text)")

        # normalize number
        if ch_number:
            try:
                new_number = int(new_number_str)
            except (TypeError, ValueError):
                print("! Ignoring number (not an integer).")
                ch_number = False

        # build dynamic update
        sets = []
        params = []
        if ch_title:
            sets.append("title = %s");            params.append(new_title)
        if ch_number:
            sets.append("number = %s");           params.append(int(new_number_str))
        if ch_category:
            sets.append("category = %s");         params.append(new_category)
        if ch_pinned:
            sets.append("pinned = %s");           params.append(new_pinned)
        if ch_tags:
            sets.append("tags = %s");             params.append(new_tags)
        if ch_content:
            sets.append("content = %s");          params.append(new_content)

        if not sets:
            print("No changes provided. Nothing to update.")
            return

        sets.append("updated_at = now()")
        params.append(nid)

        cur.execute(f"""
            UPDATE notes
               SET {", ".join(sets)}
             WHERE id = %s
         RETURNING id, code, number, title, category, pinned, updated_at;
        """, params)
        res = cur.fetchone()
        if not res:
            print("Update failed: note not found after update.")
            return
        conn.commit()
        cur.close()

    print(f"✅ Updated note id={res[0]} code={res[1]} number={res[2]} title='{res[3]}' "
          f"category={res[4]} pinned={res[5]} (updated_at {res[6]})")

if __name__ == "__main__":
    main()
