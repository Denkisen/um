from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.Sankaku2 import DowSankaku
from classes.Pixiv import DowPixiv
from classes.Worker import DowWorker
from classes.MimeType import DowMimeType
import pathlib
from multiprocessing import Process

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME, False)
download_dir = pathlib.Path(config.ROOT_DIR).joinpath(config.DOWNLOAD_FOLDER)
sankaku = DowSankaku(config.SAN_USER, config.SAN_PASSWORD, download_dir, config.SAN_USER_TAG)
pixiv = DowPixiv(download_dir, config.PIXIV_TOKEN)

procs = []

def file_in_db(module, file):
  return True

def file_no_in_db(module, file):
  module.DeleteBookmark(file)
  return True


procs.append(Process(target=DowWorker().Worker, args=(sankaku, db, file_in_db, file_no_in_db,)))
procs.append(Process(target=DowWorker().Worker, args=(pixiv, db, file_in_db, file_no_in_db,)))
for proc in procs:
  proc.start()

for proc in procs:
  proc.join()