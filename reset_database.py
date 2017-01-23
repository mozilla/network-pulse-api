import glob, os, subprocess

"""
Reset the database to a shiny new database with minimal-step
migrations to get all models inserted as tables.
"""

# remove old migrations
for f in glob.glob("pulseapi/**/migrations/00*.py"):
  if 'issues' not in f:
    os.remove(f)

# remove old database
try:
  os.remove('db.sqlite3')
except:
  pass

# make and apply migrations
subprocess.run(["python", "manage.py", "makemigrations"])
subprocess.run(["python", "manage.py", "migrate"])
