import json

class DowConfig():
  def __init__(self):
    f = open("config.json", "r")
    conf = json.load(f)
    self.DB_PATH = conf["DB_PATH"]
    self.DB_NAME = conf["DB_NAME"]
    self.DUPS = conf["DUPS"]
    self.MAP_NAME = conf["MAP_NAME"]
    self.DOWNLOAD_DIR = conf["DOWNLOAD_DIR"]
    self.SORT_DEST_DIR = conf["SORT_DEST_DIR"]
    self.SAN_USER = conf["SAN_USER"]
    self.SAN_PASSWORD = conf["SAN_PASSWORD"]
    self.SAN_USER_TAG = conf["SAN_USER_TAG"]
    self.SLIDE_CONFIG = conf["SLIDE_CONFIG"]
    self.PIXIV_TOKEN = conf["PIXIV_TOKEN"]
    f.close()
