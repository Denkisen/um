import os
import sqlite3

class DowDatabase():
  def __init__(self, db_path, db_name):
    os.makedirs(db_path, exist_ok=True)
    if not os.path.exists(os.path.join(db_path, db_name)):
      self.__make_db(db_path, db_name)

    self.__db = sqlite3.connect(os.path.join(db_path, db_name))
    self.__db_cur = self.__db.cursor()

  def __del__(self):
    self.__db.close()

  def __make_db(self, db_path, db_name):
    db = sqlite3.connect(os.path.join(db_path, db_name))
    db_cur = db.cursor()
    db_cur.execute("CREATE TABLE files (name text, path text, tags text, features text)")
    db.close()

  def Insert(self, name, path, tags, features = "no"):
    sql = "INSERT INTO files VALUES ('%s','%s','%s','%s')" % (name, path, tags, features)
    self.__db_cur.execute(sql)
    self.__db.commit()
  
  def Delete(self, name):
    sql = "DELETE FROM files WHERE name = '%s'" % name
    self.__db_cur.execute(sql)
    self.__db.commit()
  
  def Update(self, name, field, value):
    sql = "UPDATE files SET %s = '%s' WHERE name = '%s'" % (field, value, name)
    self.__db_cur.execute(sql)
    self.__db.commit()
  
  def IsFileIn(self, name):
    sql = "SELECT name FROM files WHERE name = '%s'" % name
    self.__db_cur.execute(sql)
    self.__db.commit()
    return self.__db_cur.fetchone() is not None
  
  def IsFileInLike(self, name):
    sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + name + '%')
    self.__db_cur.execute(sql)
    self.__db.commit()
    return self.__db_cur.fetchone() is not None

  def SelectFile(self, name):
    sql = "SELECT * FROM files WHERE name = '%s'" % name
    self.__db_cur.execute(sql)
    self.__db.commit()
    return self.__db_cur.fetchone()

  def SelectAll(self):
    sql = "SELECT * FROM files"
    return self.Execute(sql)

  def Execute(self, sql):
    self.__db_cur.execute(sql)
    self.__db.commit()
    return self.__db_cur.fetchall()