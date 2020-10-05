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
sql = "SELECT * FROM files"
db_cur.execute(sql)
db.commit()

data = db_cur.fetchall()

if data is None or len(data) == 0:
  sys.exit(0)

for line in data:
  name, path, tags, features = line
  path = str (path).replace("nice2", "nice3")
  
  if not os.path.exists(os.path.join(path, name)):
    sql = "DELETE FROM files WHERE name = '%s'" % name
  #else:
    #sql = "UPDATE files SET path = '%s' WHERE name = '%s'" % (path, name)

    db_cur.execute(sql)
    db.commit()

db.close()