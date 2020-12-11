import sqlite3
import os
import io
import glob
import json

DB_NAME = ''
DB_PATH = ''

f = open("config.json", "r")
conf = json.load(f)
DB_NAME = conf["DB_NAME"]
DB_PATH = conf["DB_PATH"]
f.close()

def connect(path, db_name):
  db = sqlite3.connect(os.path.join(path, db_name))
  db_cur = db.cursor()
  return db, db_cur

def commit_to_table(db):
  db.commit()

def make_table(db_cur, files_dir, table_name, fields):
  sch = ",".join(fields)
  db_cur.execute("""CREATE TABLE %s (%s)""" % (table_name, sch))

def insert_in_table(db_cur, table_name, data):
  for f in range(0, len (data)):
    data[f] = data[f].replace("'", "''")
  sch = "'" + "','".join(data) + "'"
  db_cur.execute("""INSERT INTO %s VALUES (%s)""" % (table_name, sch))

def check_value(db, db_cur, table_name, field_name, value):
  sql = """SELECT * FROM %s WHERE %s = '%s'""" % (table_name, field_name, value)
  db_cur.execute(sql)
  db.commit()
  data = db_cur.fetchone()
  return data is not None

def update_record_in_table(db_cur, table_name, key_field_name, src_field_name, key_field_value, new_src_field_value):
  db_cur.execute("""UPDATE %s SET %s = '%s' WHERE %s = '%s'""" % (table_name, src_field_name, new_src_field_value, key_field_name, key_field_value))

db, db_cur = connect(DB_PATH, DB_NAME)
make_table(db_cur, DB_PATH, "files", ["name text", "path text, tags text, features text"])
