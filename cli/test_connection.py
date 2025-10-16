import os
import ssl
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import pg8000

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# Parse the postgres URI
u = urlparse(DATABASE_URL)
db = (u.path or "").lstrip("/")
q = parse_qs(u.query)

# SSL required for Neon; create a default SSL context
ssl_ctx = ssl.create_default_context()

print("Connecting to Neon...")

try:
    conn = pg8000.connect(
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
        database=db,
        ssl_context=ssl_ctx,   # enforce TLS
    )
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user, version();")
    dbname, dbuser, version = cur.fetchone()
    print("Connected successfully!")
    print("Database:", dbname)
    print("User:", dbuser)
    print("PostgreSQL version:", version.splitlines()[0])
    cur.close()
    conn.close()
except Exception as e:
    print("Connection failed:", repr(e))
