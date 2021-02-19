from Config import DowConfig
from Database import DowDatabase
from Sankaku import DowSankaku
from Pixiv import DowPixiv
from Tags import DowTags
import sys
import os
import pathlib
from multiprocessing import Process
from collections import defaultdict

config = DowConfig()
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)
sankaku = DowSankaku(config.SAN_USER, config.SAN_PASSWORD, os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER), config.SAN_USER_TAG)
pixiv = DowPixiv(os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER), config.PIXIV_TOKEN)
tags = DowTags(os.path.join(config.ROOT_DIR, config.WHITE_LIST))

procs = []
restore_db = False

if not sankaku.IsConnected():
  sys.exit(1)

def SankakuWorker(rest_db):
  while sankaku.GetNextPage():
    for i in range(0, sankaku.GetFilesLen()):
      file = sankaku.GetFile(i)
      if file is None:
        return
      if not db.IsFileIn(file[1][0]):
        if not rest_db:
          if sankaku.DownloadFile(file):
            print("Insert to db: %s" % file[1][0])
            db.Insert(file[1][0], os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER), file[2])
        else:
          path = pathlib.Path(config.ROOT_DIR).glob("**/%s" % file[1][0])
          for f in path:
            print("Insert to db: %s" % str(f))
            f = pathlib.Path(f.parents[0])
            db.Insert(file[1][0], f, file[2])
      else:
        if rest_db:
          continue
        else:
          print("File exists, return")
          return
  print("End of Sankaku worker")

def PixivWorker(rest_db):
  while pixiv.GetNextPage():
    for i in range(0, pixiv.GetFilesLen()):
      file = pixiv.GetFile(i)
      if file is None:
        return
      if not rest_db:
        short_f = pixiv.GetShortFileName(file)
        if not db.IsFileInLike(short_f):
          if pixiv.DownloadFile(file):
            if len(file[1]) > 1:
              for f in file[1]:
                print("Insert to db: %s" % f)
                db.Insert(f, os.path.join(os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER), short_f), file[2])
            else:
              print("Insert to db: %s" % file[1][0])
              db.Insert(file[1][0], os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER), file[2])
        else:
          print("File exists, return")
          return
      else:
        if len(file[1]) > 1:
          for f in file[1]:
            path = pathlib.Path(config.ROOT_DIR).glob("**/%s" % f)
            for p in path:
              if not db.IsFileIn(f):
                print("Insert to db: %s" % p)
                p = pathlib.Path(p.parents[0])
                db.Insert(f, p, file[2])
  print("End of Pixiv worker")

def GetAllTags():
  all_tags = defaultdict(int)
  data = db.Execute("SELECT tags FROM files")
  for line in data:
    spt = str(line[0]).split(" ")
    for tag in spt:
      all_tags[tag] += 1

  f = open(os.path.join(config.ROOT_DIR, "tags.txt"), "w")
  for t in sorted(all_tags.items(), key=lambda item: item[1]):
    f.write("%s %s\n" % (t[0], t[1]))
  f.close()

def FixPixivPath():
  data = db.Execute("SELECT name,path FROM files WHERE path != '%s'" % os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER))
  if data is not None:
    for line in data:
      if "_" not in line[0]:
        db.Update(line[0], "path", os.path.join(config.ROOT_DIR, config.DOWNLOAD_FOLDER))

procs.append(Process(target=SankakuWorker, args=(restore_db,)))
procs.append(Process(target=PixivWorker, args=(restore_db,)))
procs[0].start()
procs[1].start()
# for proc in procs:
#   proc.join()
#FixPixivPath()
# GetAllTags()
