import os
import sys
import shutil
import sqlite3
import json

DB_PATH = ""
DB_NAME = ""
DOWNLOAD_DIR = ""

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
DOWNLOAD_DIR = conf["DOWNLOAD_DIR"]
f.close()

db = sqlite3.connect(os.path.join(DB_PATH, DB_NAME))
db_cur = db.cursor()

sql = "SELECT * FROM files WHERE tags LIKE '%s'" %  ("%" + sys.argv[1] + "%")
db_cur.execute(sql)
db.commit()

data = db_cur.fetchall()

if data is None or len(data) == 0:
  sys.exit(0)

for line in data:
  name, path, tags, features = line
  move_dir = DOWNLOAD_DIR
  shutil.move(os.path.join(path, name), os.path.join(move_dir, name))
  sql = "UPDATE files SET path = '%s' WHERE name = '%s'" % (move_dir, name)
  db_cur.execute(sql)
  db.commit()

db.close()