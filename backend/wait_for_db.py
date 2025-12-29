import os
import time
import sys
from urllib.parse import urlparse

import psycopg2
from psycopg2 import OperationalError
import shlex
import subprocess


def wait_for_db(url, timeout=60):
    # Accept SQLAlchemy-style URL like postgresql+psycopg2://user:pass@host:port/db
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql://")
    parsed = urlparse(url)
    host = parsed.hostname or os.getenv('DB_HOST', 'db')
    port = parsed.port or 5432
    user = parsed.username or os.getenv('POSTGRES_USER')
    password = parsed.password or os.getenv('POSTGRES_PASSWORD')
    dbname = (parsed.path[1:] if parsed.path else os.getenv('POSTGRES_DB', 'postgres'))

    start = time.time()
    while True:
        try:
            conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname, connect_timeout=5)
            conn.close()
            print("Database reachable")
            return True
        except OperationalError as e:
            elapsed = time.time() - start
            if elapsed > timeout:
                print("Timeout waiting for database:", e)
                return False
            print("Waiting for database...", str(e))
            time.sleep(2)


if __name__ == '__main__':
    db_url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://gitlite:gitlite@db:5432/gitlite')
    timeout = int(os.getenv('DB_WAIT_TIMEOUT', '60'))
    ok = wait_for_db(db_url, timeout=timeout)
    if not ok:
        print('Database did not become ready, exiting')
        sys.exit(1)

    # start the server
    start_cmd = os.getenv('START_CMD') or f"uvicorn app.main:app --host 0.0.0.0 --port {os.getenv('WEB_PORT','8080')}"
    print('Starting server with:', start_cmd)
    args = shlex.split(start_cmd)
    os.execvp(args[0], args)
