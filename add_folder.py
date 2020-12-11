import os
import sys
import shutil
import sqlite3
import json

DB_PATH = ""
DB_NAME = ""

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
f.close()

db = sqlite3.connect(os.path.join(DB_PATH, DB_NAME))
db_cur = db.cursor()
tags = "tagme"

for root, directories, filenames in os.walk(sys.argv[1]):
  print("Dir: %s" % sys.argv[1])
  for filename in filenames:
    print("File: %s" % filename)
    if str.lower(os.path.splitext(filename)[-1]) in ['.bmp', '.jpg', '.jpeg', '.png', '.gif', '.webm', '.mp4']:
      sql = "SELECT * FROM files WHERE name = '%s'" % filename
      db_cur.execute(sql)
      db.commit()

      if db_cur.fetchone() is not None:
        continue

      sql = "INSERT INTO files VALUES ('%s','%s','%s','%s')" % (filename, root, tags, "no")
      db_cur.execute(sql)
      db.commit()

db.close()
