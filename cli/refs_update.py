# cli/refs_update.py — update reference fields by ID or CODE
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

ALLOWED_TYPES = {"article", "image", "video", "book", "other"}

def resolve_ref_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM refs WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def prompt(current, label, allow_empty_keep=True):
    shown = current if current is not None else ""
    val = input(f"{label} [{shown}] (blank = keep): ").strip()
    if val == "" and allow_empty_keep:
        return None, False  # keep
    return val, True

def main():
    ident = input("Ref (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        rid = resolve_ref_id(cur, ident)
        if not rid:
            print(f"No ref found for '{ident}'")
            return

        cur.execute("""
            SELECT id, code, project_id, creator_id, number, title, tags, type, summary, link, content
            FROM refs
            WHERE id = %s
        """, (rid,))
        row = cur.fetchone()
        if not row:
            print(f"No ref found for id={rid}")
            return

        (id_, code, project_id, creator_id, number, title, tags, rtype, summary, link, content) = row
        print("\n== Current Ref ==")
        print(f"id={id_} code={code} project_id={project_id} creator_id={creator_id}")
        print(f"number={number} title={title} type={rtype}")
        print(f"summary={summary} link={link}")
        print(f"tags={tags}")
        print("(content not shown)")

        # prompts (blank = keep)
        new_title, ch_title = prompt(title,   "New title")
        new_number_str, ch_number = prompt(number, "New number")
        new_type, ch_type = prompt(rtype, "New type (article/image/video/book/other)")
        new_summary, ch_summary = prompt(summary, "New summary")
        new_link, ch_link = prompt(link, "New link")
        new_content, ch_content = prompt("(hidden)", "New content")

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

        # normalize number / type
        if ch_number:
            try:
                new_number = int(new_number_str)
            except (TypeError, ValueError):
                print("! Ignoring number (not an integer).")
                ch_number = False

        if ch_type and new_type:
            low = new_type.lower()
            if low not in ALLOWED_TYPES:
                print(f"! Ignoring type '{new_type}'. Allowed: {', '.join(sorted(ALLOWED_TYPES))}")
                ch_type = False
            else:
                new_type = low

        # build dynamic update
        sets, params = [], []
        if ch_title:    sets.append("title = %s")   or params.append(new_title)
        if ch_number:   sets.append("number = %s")  or params.append(int(new_number_str))
        if ch_type:     sets.append("type = %s")    or params.append(new_type)
        if ch_summary:  sets.append("summary = %s") or params.append(new_summary)
        if ch_link:     sets.append("link = %s")    or params.append(new_link)
        if ch_content:  sets.append("content = %s") or params.append(new_content)
        if ch_tags:     sets.append("tags = %s")    or params.append(new_tags)

        if not sets:
            print("No changes provided. Nothing to update.")
            return

        sets.append("updated_at = now()")
        params.append(rid)

        cur.execute(f"""
            UPDATE refs
               SET {", ".join(sets)}
             WHERE id = %s
         RETURNING id, code, number, title, type, updated_at;
        """, params)
        res = cur.fetchone()
        if not res:
            print("Update failed: ref not found after update.")
            return
        conn.commit()
        cur.close()

    print(f"✅ Updated ref id={res[0]} code={res[1]} number={res[2]} title='{res[3]}' "
          f"type={res[4]} (updated_at {res[5]})")

if __name__ == "__main__":
    main()
