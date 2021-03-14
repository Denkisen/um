import pathlib
import sqlite3
from threading import Lock

class DowDatabase():
  def __init__(self, db_path, db_name, do_logs = False):
    self.__log = pathlib.Path(db_path).joinpath("db_log.txt").open("a") if do_logs else None
    pathlib.Path(db_path).mkdir(parents=True, exist_ok=True)
    if not pathlib.Path(db_path).joinpath(db_name).exists():
      self.__make_db(db_path, db_name)

    self.__db = sqlite3.connect(pathlib.Path(db_path).joinpath(db_name))
    self.__db_cur = self.__db.cursor()
    self.mutex = Lock()

  def __del__(self):
    self.mutex.acquire()
    self.__log is None or self.__log.close()
    self.__db.close()
    self.mutex.release()

  def __make_db(self, db_path, db_name):
    db = sqlite3.connect(pathlib.Path(db_path).joinpath(db_name))
    db_cur = db.cursor()
    db_cur.execute("CREATE TABLE files (name text, path text, tags text, features text)")
    db.close()

  def Insert(self, name, path, tags, features = "no"):
    sql = "INSERT INTO files VALUES ('%s','%s','%s','%s')" % (name, path, tags, features)
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    self.mutex.release()
  
  def Delete(self, name):
    sql = "DELETE FROM files WHERE name = '%s'" % name
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    self.mutex.release()
  
  def Update(self, name, field, value):
    sql = "UPDATE files SET %s = '%s' WHERE name = '%s'" % (field, value, name)
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    self.mutex.release()
  
  def IsFileIn(self, name):
    sql = "SELECT name FROM files WHERE name = '%s'" % name
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchone() is not None
    self.mutex.release()
    return ret
  
  def IsFileInLike(self, name):
    sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + name + '%')
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchone() is not None
    self.mutex.release()
    return ret

  def SelectFile(self, name):
    sql = "SELECT * FROM files WHERE name = '%s'" % name
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchone()
    self.mutex.release()
    return ret

  def SelectFileLike(self, name):
    sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + name + '%')
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchone()
    self.mutex.release()
    return ret

  def SelectAllFilesLike(self, name):
    sql = "SELECT * FROM files WHERE name LIKE '%s'" % ('%' + name + '%')
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchall()
    self.mutex.release()
    return ret if len(ret) > 0 else None

  def SelectAll(self):
    sql = "SELECT * FROM files"
    return self.Execute(sql)

  def Execute(self, sql):
    self.mutex.acquire()
    self.__log is None or self.__log.write(sql + "\n")
    self.__db_cur.execute(sql)
    self.__db.commit()
    ret = self.__db_cur.fetchall()
    self.mutex.release()
    return ret