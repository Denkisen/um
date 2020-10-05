import io
import os
import sys
import sqlite3
import json
from pathlib import Path
from pixivapi import Size
from pixivapi import Client

DOWNLOAD_DIR = ""
DB_PATH = ""
DB_NAME = ""
PIXIV_TOKEN = ""

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
DOWNLOAD_DIR = Path(conf["DOWNLOAD_DIR"])
PIXIV_TOKEN = conf["PIXIV_TOKEN"]
f.close()

client = Client()
client.authenticate(PIXIV_TOKEN)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

db = sqlite3.connect(os.path.join(DB_PATH, DB_NAME))
db_cur = db.cursor()

response = client.fetch_user_bookmarks(client.account.id)
offset = response['next']
skip = False
while True:
  
  for ill in response['illustrations']:
    sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + str (ill.id) + '%')
    db_cur.execute(sql)
    db.commit()
    
    # if ill.id == 84310892:
      # skip = False
      
    if db_cur.fetchone() is not None:
      if skip:
        continue
      else:
        db.close()
        sys.exit(0)

    tags = ill.user.name
    tags += " " + ill.user.account
    for tag in ill.tags:
      if tag['translated_name'] is not None:
        tags += " " + str (tag['translated_name']).replace(' ', '_').replace("'", "''")

    file_name = []
    if ill.page_count == 1:
      file_name.append(str (ill.image_urls[Size.ORIGINAL]).split('/')[-1].replace("_p0", ""))

    for p in ill.meta_pages:
      file_name.append(str (p[Size.ORIGINAL]).split('/')[-1])
    

    ill.download(directory=DOWNLOAD_DIR, size=Size.ORIGINAL)

    sql = ""
    for s in file_name:
      dow_dir = DOWNLOAD_DIR
      if len (file_name) > 1:
        dow_dir = os.path.join(dow_dir, str (ill.id))

      if os.path.exists(os.path.join(dow_dir, s)):
        sql = "INSERT INTO files VALUES ('%s','%s','%s','%s')" % (s, dow_dir, tags, "no")
        db_cur.execute(sql)
    db.commit()

  if not response['next']:
    break

  response = client.fetch_user_bookmarks(client.account.id, max_bookmark_id=int (response['next']))

db.close()
