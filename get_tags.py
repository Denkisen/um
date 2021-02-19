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
sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + sys.argv[1] + '%')
db_cur.execute(sql)
db.commit()
o = db_cur.fetchone()
if o is not None:
  print(o[2])
else:
  print("None")
db.close()

