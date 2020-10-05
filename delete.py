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
sql = "SELECT path FROM files WHERE name = '%s'" % sys.argv[1]
db_cur.execute(sql)
db.commit()

path = db_cur.fetchone()[0]
sql = "DELETE FROM files WHERE name = '%s'" % sys.argv[1]
print(sql)

os.remove(os.path.join(path, sys.argv[1]))
db_cur.execute(sql)
db.commit()

db.close()