# cli/chapters_update.py — update chapter fields by ID or CODE
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from inkdb.db import get_conn

ALLOWED_STATUS = {"draft", "final"}

def resolve_chapter_id(cur, token: str):
    if token.isdigit():
        return int(token)
    cur.execute("SELECT id FROM chapters WHERE code = %s;", (token,))
    row = cur.fetchone()
    return row[0] if row else None

def prompt(current, label, allow_empty_keep=True):
    val = input(f"{label} [{current if current is not None else ''}] (blank = keep): ").strip()
    if val == "" and allow_empty_keep:
        return None, False  # keep existing
    return val, True

def main():
    ident = input("Chapter (ID or CODE): ").strip()
    with get_conn() as conn:
        cur = conn.cursor()

        # Load current row
        chap_id = resolve_chapter_id(cur, ident)
        if not chap_id:
            print(f"No chapter found for '{ident}'")
            return

        cur.execute("""
            SELECT id, code, project_id, creator_id, number, title, content, status, summary, tags
            FROM chapters
            WHERE id = %s
        """, (chap_id,))
        row = cur.fetchone()
        if not row:
            print(f"No chapter found for id={chap_id}")
            return

        (cid, code, project_id, creator_id, number, title, content, status, summary, tags) = row
        print("\n== Current Chapter ==")
        print(f"id={cid} code={code} project_id={project_id} creator_id={creator_id}")
        print(f"number={number} title={title}")
        print(f"status={status} summary={summary}")
        print(f"tags={tags}")
        print("(content not shown)")

        # Prompts — blank means “keep existing”
        new_title, ch_title = prompt(title,   "New title")
        new_number_str, ch_number = prompt(number, "New number")
        new_status, ch_status = prompt(status, "New status (draft/final)")
        new_summary, ch_summary = prompt(summary, "New summary")
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

        # Content prompt (optional)
        new_content, ch_content = prompt("(hidden)", "New content (full text)")

        # Normalize number / status
        if ch_number:
            if new_number_str == "":
                ch_number = False
            else:
                try:
                    new_number = int(new_number_str)
                except ValueError:
                    print("! Ignoring number (not an integer).")
                    ch_number = False
        if ch_status and new_status:
            if new_status.lower() not in ALLOWED_STATUS:
                print("! Ignoring status (must be 'draft' or 'final').")
                ch_status = False
            else:
                new_status = new_status.lower()

        # Build dynamic update
        sets = []
        params = []
        if ch_title:
            sets.append("title = %s")
            params.append(new_title)
        if ch_number:
            sets.append("number = %s")
            params.append(int(new_number_str))
        if ch_status:
            sets.append("status = %s")
            params.append(new_status)
        if ch_summary:
            sets.append("summary = %s")
            params.append(new_summary)
        if ch_tags:
            sets.append("tags = %s")
            params.append(new_tags)
        if ch_content:
            sets.append("content = %s")
            params.append(new_content)

        if not sets:
            print("No changes provided. Nothing to update.")
            return

        sets.append("updated_at = now()")
        params.append(chap_id)

        cur.execute(f"""
            UPDATE chapters
               SET {", ".join(sets)}
             WHERE id = %s
         RETURNING id, code, number, title, status, updated_at;
        """, params)
        res = cur.fetchone()
        if not res:
            print("Update failed: chapter not found after update.")
            return
        conn.commit()
        cur.close()

    print(f"✅ Updated chapter id={res[0]} code={res[1]} number={res[2]} title='{res[3]}' status={res[4]} (updated_at {res[5]})")

if __name__ == "__main__":
    main()
