#!/bin/sh
set -eu

python - <<'PY'
import sys
import time

import django
from django.db import connections
from django.db.utils import OperationalError

django.setup()
database = connections["default"]

for attempt in range(1, 31):
    try:
        database.ensure_connection()
    except OperationalError as error:
        if attempt == 30:
            print(
                "Database did not become available after 60 seconds: "
                f"{error.__class__.__name__}",
                file=sys.stderr,
            )
            raise SystemExit(1) from error
        print(f"Waiting for database ({attempt}/30)...", flush=True)
        time.sleep(2)
    else:
        print("Database connection is ready.", flush=True)
        database.close()
        break
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
