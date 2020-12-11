import tensorflow as tf
import numpy as np
import keras
import cv2
import os
import random
import glob
import shutil
import sqlite3
import json

from datetime import datetime
from itertools import repeat
from keras.applications import VGG19
from keras.engine import Model
from keras.preprocessing import image
from keras.applications.vgg19 import preprocess_input
from sklearn.neighbors import NearestNeighbors

DB_NAME = ''
DB_PATH = ''
DUPS = ''

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
DUPS = conf["DUPS"]
f.close()

log = open("log.txt", "w")

def make_model():
    return VGG19(weights='imagenet', include_top=False)

def load_image(file_name):
    img = image.load_img(file_name, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    return preprocess_input(x)

def get_features(file_name, model):
    return model.predict(load_image(file_name)).ravel()

def build_db_of_features(dir, db_name, model):
    db = sqlite3.connect(os.path.join(dir, db_name))
    db_cur = db.cursor()
    for filename in glob.iglob(os.path.join(dir, '**/*.*'), recursive=True):
        file, ext = os.path.splitext(filename)
        if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            sql = "SELECT * FROM files WHERE name = '%s'" % filename.split("/")[-1]
            db_cur.execute(sql)
            db.commit()
            val = db_cur.fetchone()
            if val is None:
                print ("Error: " + filename)
                exit()
            if val[3] != 'no':
                continue
            try:
                features = get_features(filename, model)
            except:
                print("Error: " + filename)
                log.write(filename + "\n")
                continue
            st = ' '.join(str(x) for x in features)
            sql = "UPDATE files SET features = '%s' WHERE name = '%s'" % (st, filename.split("/")[-1])
            db_cur.execute(sql)
            db.commit()
    db.close()

def load_features_from_db(file_name):
    db = sqlite3.connect(file_name)
    db_cur = db.cursor()
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
    db.close()
    return files, features

def load_comparator(features):
    knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
    knn.fit(features)
    return knn

def find_dups_in_dir(input_dir, output_dir):
    model = make_model()
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    build_db_of_features(input_dir, DB_NAME, model)
    files, features = load_features_from_db(os.path.join(input_dir, DB_NAME))
    knn = load_comparator(features)
    dups = open(os.path.join(output_dir, DUPS), "w")
    for i in range(0, len(files)):
        dist, indices = knn.kneighbors(features[i].reshape(1, -1), n_neighbors=5)
        for j in indices[0]:
            if files[indices[0][list(indices[0]).index(j)]] == files[i]:
                continue
            if dist[0][list(indices[0]).index(j)] < 0.4:
                dups.write("%s | %s\n" % (files[indices[0][list(indices[0]).index(j)]], files[i]))
    dups.close()


find_dups_in_dir(DB_PATH, DB_PATH)


