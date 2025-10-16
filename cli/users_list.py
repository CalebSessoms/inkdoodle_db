# users_list.py — list users (active first)
from db_conn import get_conn

with get_conn() as conn:
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, display_name, is_active, created_at
        FROM users
        ORDER BY is_active DESC, id ASC
        LIMIT 50;
    """)
    cols = [d[0] for d in cur.description]
    print(" | ".join(cols))
    for row in cur.fetchall():
        print(" | ".join(str(x) for x in row))
    cur.close()
