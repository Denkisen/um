import json
import pathlib

class DowConfig():
  def __init__(self, config_file_path):
    f = pathlib.Path(config_file_path).open("r")
    conf = json.load(f)
    self.DB_NAME = conf["DB_NAME"]
    self.DUPS = conf["DUPS"]
    self.MAP_NAME = conf["MAP_NAME"]
    self.DOWNLOAD_FOLDER = conf["DOWNLOAD_FOLDER"]
    self.ROOT_DIR = conf["ROOT_DIR"]
    self.ERROR_FOLDER = conf["ERROR_FOLDER"]
    self.SAN_USER = conf["SAN_USER"]
    self.SAN_PASSWORD = conf["SAN_PASSWORD"]
    self.SAN_USER_TAG = conf["SAN_USER_TAG"]
    self.SLIDE_CONFIG = conf["SLIDE_CONFIG"]
    self.PIXIV_TOKEN = conf["PIXIV_TOKEN"]
    self.WHITE_LIST = conf["WHITE_LIST"]
    self.ADD_FOLDER = conf["ADD_FOLDER"]
    self.UNSORTED_FOLDER = conf["UNSORTED_FOLDER"]
    f.close()
