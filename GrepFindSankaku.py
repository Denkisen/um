import requests
import time
import io
import os
import sys
import AdvancedHTMLParser
import json
import sqlite3
import tensorflow as tf
import numpy as np
import keras
import cv2
import random
import glob
import shutil

from datetime import datetime
from itertools import repeat
from keras.applications import VGG19
from keras.engine import Model
from keras.preprocessing import image
from keras.applications.vgg19 import preprocess_input
from sklearn.neighbors import NearestNeighbors

URL = "https://chan.sankakucomplex.com"
DOWNLOAD_DIR = ""
DB_PATH = ""
DB_NAME = ""
SAN_USER = ""
SAN_PASSWORD = ""
SAN_USER_TAG = ""
HTTP_HEADERS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40"

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
SAN_USER = conf["SAN_USER"]
SAN_PASSWORD = conf["SAN_PASSWORD"]
DOWNLOAD_DIR = conf["DOWNLOAD_DIR"]
SAN_USER_TAG = conf["SAN_USER_TAG"]
f.close()

log = open("log.txt", "w")
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "New")

values = {
  'url' : "/user/home",
  'user[name]': SAN_USER,
  'user[password]': SAN_PASSWORD,
  'commit' : "Login"
}

def make_model():
  return VGG19(weights='imagenet', include_top=False)

def load_image(file_name):
  img = image.load_img(file_name, target_size=(224, 224))
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  return preprocess_input(x)

def get_features(file_name, model):
  return model.predict(load_image(file_name)).ravel()

def load_comparator(features):
  knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
  knn.fit(features)
  return knn

def get_features_from_db(db, db_cur, file_name):
  file, ext = os.path.splitext(file_name)
  features = []
  if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
    sql = "SELECT * FROM files WHERE name = '%s'" % file_name.split("/")[-1]
    db_cur.execute(sql)
    db.commit()
    val = db_cur.fetchone()
    if val is None:
      print ("Error: " + file_name)
      exit()

    if val[3] != 'no':
      fts = np.array(list(map(np.float, val[3].split(' '))))
      features = fts
    else:
      try:
        features = get_features(file_name, model)
        st = ' '.join(str(x) for x in features)
        sql = "UPDATE files SET features = '%s' WHERE name = '%s'" % (st, filename.split("/")[-1])
        db_cur.execute(sql)
        db.commit()
      except:
        print("Error: " + file_name)
        log.write(file_name + "\n")
  return features


def load_features_from_db(db, db_cur, file_name):
  sql = "SELECT * FROM files WHERE NOT features = 'no'"
  db_cur.execute(sql)
  db.commit()
  data = db_cur.fetchall()
  files = []
  features = []
  for line in data:
    files.append(os.path.join(line[1], line[0]))
    fts = np.array(list(map(np.float, line[3].split(' '))))
    features.append(fts)

  return files, features

def get_request(s, text, istream=False):
  resp = ""
  try:
    time.sleep(5)
    resp = s.get(text, stream=istream)
    while resp.status_code == 500 or resp.status_code == 429:
      print("Wait")
      time.sleep(60)
      resp = s.get(text, stream=istream)
  except:
    time.sleep(30)
    resp = s.get(text, stream=istream)
  
  return resp

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

db = sqlite3.connect(os.path.join(DB_PATH, DB_NAME))
db_cur = db.cursor()
s = requests.Session()
s.headers['User-Agent'] = HTTP_HEADERS

response = get_request(s, URL + '/user/login')
response = s.post(URL + '/user/authenticate', data=values)

if "My Account" in response.text:
  i = 1
  model = make_model()

  while response.status_code == 200:
    print("Page:%s" % str (i))
    response = get_request(s, URL + "/?tags=fav" +"%3A" + SAN_USER_TAG + "&" + "page=%s" % str (i))

    i += 1
    if response.status_code != 200:
      break
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(response.text)
    spans = parser.getElementsByTagName('span').getElementsByClassName('thumb')
    if len(spans) == 0:
      db.close()
      sys.exit(0)
    for sp in spans:
      item = sp[0]
      img = item[0]
      prev_file_name = str (img.src).split("/")[-1]
      sql = "SELECT * FROM files WHERE name = '%s'" % prev_file_name
      db_cur.execute(sql)
      db.commit()
      
      if db_cur.fetchone() is not None:
        #db.close()
        #sys.exit(0)
        continue

      if 'plus' in item.href:
        continue

      resp = get_request(s, URL + item.href)
      
      ps = AdvancedHTMLParser.AdvancedHTMLParser()
      ps.parseStr(resp.text)
      link = ps.getElementsByTagName('a').getElementById('highres')
      name = os.path.join(DOWNLOAD_DIR ,prev_file_name)
      data = get_request(s, "https:" + link.href, True)

      if data.status_code == 200:
        open(name, "bw").write(data.content)
        print("File:%s" % name)
        tags = " ".join(str(img.title).replace("'", "''").split(" ")[:-4])
        sql = "INSERT INTO files VALUES ('%s','%s','%s','%s')" % (prev_file_name, DOWNLOAD_DIR, tags, "no")
        db_cur.execute(sql)
        db.commit()
        features = get_features_from_db(db, db_cur, prev_file_name)

db.close()