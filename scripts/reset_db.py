import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# scripts/reset_db.py
from inkdb.db import get_conn
from pathlib import Path

SCHEMA_FILE = Path("sql/schema.sql").read_text()

SQL_DROP = """
DROP TABLE IF EXISTS refs CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS chapters CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS creators CASCADE;
"""

if __name__ == "__main__":
    with get_conn() as conn:
        cur = conn.cursor()
        print("Dropping existing tables (if any)...")
        cur.execute(SQL_DROP)
        print("Rebuilding schema...")
        cur.execute(SCHEMA_FILE)
        conn.commit()
        cur.close()
        print("✅ Database reset complete and schema rebuilt.")
