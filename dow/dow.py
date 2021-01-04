from Config import DowConfig
from Database import DowDatabase
from Sankaku import DowSankaku
from Pixiv import DowPixiv
import sys
import os
from multiprocessing import Process

config = DowConfig()
db = DowDatabase(config.DB_PATH, config.DB_NAME)
sankaku = DowSankaku(config.SAN_USER, config.SAN_PASSWORD, config.DOWNLOAD_DIR, config.SAN_USER_TAG)
pixiv = DowPixiv(config.DOWNLOAD_DIR, config.PIXIV_TOKEN)

procs = []

if not sankaku.IsConnected():
  sys.exit(1)

def SankakuWorker():
  while sankaku.GetNextPage():
    for i in range(0, sankaku.GetFilesLen()):
      file = sankaku.GetFile(i)
      if file is None:
        return
      if not db.IsFileIn(file[1][0]):
        if sankaku.DownloadFile(file):
          db.Insert(file[1][0], config.DOWNLOAD_DIR, file[2])

def PixivWorker():
  while pixiv.GetNextPage():
    for i in range(0, pixiv.GetFilesLen()):
      file = pixiv.GetFile(i)
      if file is None:
        return
      short_f = pixiv.GetShortFileName(file)
      if not db.IsFileInLike(short_f):
        if pixiv.DownloadFile(file):
          for f in file[1]:
            db.Insert(f, os.path.join(config.DOWNLOAD_DIR, short_f), file[2])

procs.append(Process(target=SankakuWorker, args=()))
procs.append(Process(target=PixivWorker, args=()))
procs[0].start()
procs[1].start()

for proc in procs:
  proc.join()