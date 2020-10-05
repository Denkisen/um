import os
import sys
import shutil
import sqlite3
import json

MAP_NAME = ""
DB_PATH = ""
DB_NAME = ""
DOWNLOAD_DIR = ""
SORT_DEST_DIR = ""

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
MAP_NAME = conf["MAP_NAME"]
DOWNLOAD_DIR = conf["DOWNLOAD_DIR"]
SORT_DEST_DIR = conf["SORT_DEST_DIR"]
f.close()

db = sqlite3.connect(os.path.join(DB_PATH, DB_NAME))
db_cur = db.cursor()
mapping = open(os.path.join(DB_PATH, MAP_NAME), "r")

sql = "SELECT * FROM files"
db_cur.execute(sql)
db.commit()
data = db_cur.fetchall()

if data is None or len(data) == 0:
  sys.exit(0)

for line in data:
  name, path, tags, features = line

  if name == "59268395.jpg":
    name = name

  if not os.path.exists(os.path.join(path, name)):
    sql = "DELETE FROM files WHERE name = '%s'" % name
    db_cur.execute(sql)
    db.commit()
    continue

  tags = tags.split(" ")
  mapping.seek(0)
  done = False
  for m in mapping:
    if m == "\n": continue

    folder, ts = m.split(":", 2)
    ts = ts[:-1]
    ts = ts.split(",")
    finded = False
    for t in ts:
      finded = t in tags
      if finded: break
    if finded:
      done = True
      move_dir = os.path.join(SORT_DEST_DIR, folder)
      if move_dir == path:
        break

      os.makedirs(move_dir, exist_ok=True)
      shutil.move(os.path.join(path, name), os.path.join(move_dir, name))
      sql = "UPDATE files SET path = '%s' WHERE name = '%s'" % (move_dir, name)
      db_cur.execute(sql)
      db.commit()
      break
  
  move_dir = DOWNLOAD_DIR
  if not done and path != move_dir:
    shutil.move(os.path.join(path, name), os.path.join(move_dir, name))
    sql = "UPDATE files SET path = '%s' WHERE name = '%s'" % (move_dir, name)
    db_cur.execute(sql)
    db.commit()



mapping.close()
db.close()
