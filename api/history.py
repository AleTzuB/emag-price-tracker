import os, json
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Request

DB_URL = os.environ["POSTGRES_URL"]

def handler(request):
    req = Request(request.environ)
    pid = req.args.get("id")
    if not pid:
        return ("Missing 'id' query parameter", 400)

    conn = psycopg2.connect(DB_URL, sslmode="require", cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM prices WHERE product_id = %s ORDER BY created_at ASC", (pid,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return (json.dumps(rows, default=str), 200, {"Content-Type": "application/json"})
