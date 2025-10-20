# cli/schema_report.py — prints current Neon table/column info
from inkdb.db import get_conn

SQL = """
SELECT
  c.table_name,
  c.column_name,
  c.data_type,
  c.is_nullable,
  c.column_default
FROM information_schema.columns c
WHERE c.table_schema = 'public'
  AND c.table_name IN ('users','works','chapters','notes','refs')
ORDER BY c.table_name, c.ordinal_position;
"""

if __name__ == "__main__":
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(SQL)
        rows = cur.fetchall()
        cur.close()

    current = None
    for t, col, typ, nullok, default in rows:
        if t != current:
            current = t
            print(f"\n== {t} ==")
            print("column | type | nullable | default")
        print(f"{col} | {typ} | {nullok} | {default}")
