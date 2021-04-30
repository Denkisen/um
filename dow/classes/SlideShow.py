import pathlib
from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.GlImage import DowGlImage
import threading
import time
import json

class DowSlideShow():
  def __init__(self, config : DowConfig, db : DowDatabase):
    self.__config = config
    self.__db = db
    self.__next_image_handler = None
    self.__running = False
    self.__main_visual_loop_task = threading.Thread(target=self.__main_visual_loop, args=(), daemon=True)
    self.__main_audio_loop_task = threading.Thread(target=self.__main_audio_loop, args=(), daemon=True)
    pass

  def __del__(self):
    self.__running = False

  def __main_visual_loop(self):
    while self.__running:
      time.sleep(0.1)

  def __main_audio_loop(self):
    while self.__running:
      time.sleep(0.1)