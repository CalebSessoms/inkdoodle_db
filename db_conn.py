# db_conn.py — shared Neon connection helper
import os, ssl
from urllib.parse import urlparse
from dotenv import load_dotenv
import pg8000

def get_conn():
    load_dotenv()  # loads DATABASE_URL from .env in this folder
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL missing from .env")

    u = urlparse(url)
    ssl_ctx = ssl.create_default_context()

    return pg8000.connect(
        user=u.username,
        password=u.password,
        host=u.hostname,
        port=u.port or 5432,
        database=(u.path or "").lstrip("/"),
        ssl_context=ssl_ctx,
    )
