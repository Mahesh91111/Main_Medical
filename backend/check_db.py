import os

import psycopg2
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()

url = make_url(os.environ["DATABASE_URL"])
target_db = url.database

try:
    # Connect to the default "postgres" database first, because medical_db may not exist yet
    conn = psycopg2.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        dbname="postgres",
    )
except psycopg2.OperationalError as e:
    print("CONNECTION FAILED:")
    print(e)
    raise SystemExit(1)

print(f"Connected to PostgreSQL as user '{url.username}' on {url.host}:{url.port or 5432}")

conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
if cur.fetchone():
    print(f"Database '{target_db}' already exists.")
else:
    cur.execute(f'CREATE DATABASE "{target_db}"')
    print(f"Database '{target_db}' was missing, so it has been created.")

cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY datname")
print("Databases on this server:", [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
