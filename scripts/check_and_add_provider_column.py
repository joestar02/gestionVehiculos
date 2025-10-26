import os
import sqlite3
from app.core.config import Config

c = Config()
uri = c.SQLALCHEMY_DATABASE_URI
print('DB URI:', uri)
if uri.startswith('sqlite:///'):
    path = uri.replace('sqlite:///', '')
else:
    raise SystemExit('Not sqlite')
print('DB path:', path)
if not os.path.exists(path):
    print('DB does not exist yet, nothing to modify.')
    raise SystemExit(0)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("PRAGMA table_info('maintenance_records')")
cols = cur.fetchall()
print('Columns in maintenance_records:')
for c in cols:
    print(' -', c[1], c[2])
col_names = [c[1] for c in cols]
# Ensure provider_id exists
if 'provider_id' not in col_names:
    print('provider_id missing — adding column...')
    try:
        cur.execute("ALTER TABLE maintenance_records ADD COLUMN provider_id INTEGER")
        conn.commit()
        print('Added provider_id column.')
    except Exception as e:
        print('Failed to add column:', e)
else:
    print('provider_id already exists.')
conn.close()
