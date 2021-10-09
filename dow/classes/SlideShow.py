import pathlib
from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.GlImage import DowGlImage
from classes.MimeType import DowMimeType
from PySide6 import QtCore, QtWidgets, QtGui
import threading
import time
import json
import random
import datetime

class DowSlideShow():
  def __init__(self, config : DowConfig, db : DowDatabase, script : pathlib.Path, image : DowGlImage, textbox : QtWidgets.QLabel):
    self.__config = config
    self.__db = db
    self.__files = dict()
    if self.__db != None:
      files = self.__db.SelectAll()
      for l in files:
        self.__files[l[0]] = {"Path" : l[1], "Tags" : set(str(l[2]).split(" "))}

    self.__image = image
    self.__textbox = textbox
    self.__next_image_handler = None
    self.__running = True
    self.__slide_script = script
    self.__list = []
    self.__index = 0
    self.__audio_speed = 1.0
    random.seed()
    self.__parse_script()

    self.__main_visual_loop_task = threading.Thread(target=self.__main_visual_loop, args=(), daemon=True)
    self.__main_audio_loop_task = threading.Thread(target=self.__main_audio_loop, args=(), daemon=True)
    self.__main_visual_loop_task.start()
    self.__main_audio_loop_task.start()
  
  def __del__(self):
    self.__running = False

  def __main_visual_loop(self):
    while self.__running:
      interval = 0.1
      if len(self.__list) > 0:
        item = self.__list[self.__index]
        #SetFile
        filename = pathlib.Path(item["File"])
        if self.__image != None:
          if filename.suffix in DowMimeType("").image_formats_suffix_list:
            #self.__image.SetImage(filename)
            pass
          elif filename.suffix in DowMimeType("").video_formats_suffix_list:
            #self.__image.SetVideo(filename)
            pass
        #SetText
        if self.__textbox != None:
          self.__textbox.setStyleSheet("QLabel { color : " + item["Color"] + "; font-size : " + item["Size"] + "; }")
          self.__textbox.setText(item["Text"])
        #SetSleepInterval
        interval = (datetime.datetime.strptime(item["Length"], "%H:%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()
        #SetAudioSpeed
        self.__audio_speed = item["Speed"]

      if self.__index < len(self.__list):
        self.__index += 1
      else:
        if len(self.__list) > 0:
          self.__index = 0
      time.sleep(interval)

  def __main_audio_loop(self):
    while self.__running:
      time.sleep(1 * self.__audio_speed)

  def __parse_script(self):
    self.__list = []
    self.__index = 0
    if self.__slide_script != None:
      js = json.loads(self.__slide_script.read_text())
      if js["Type"] == "Script":
        self.__script_type_parser(js["Parts"])
      elif js["Type"] == "Random":
        self.__random_type_parser(js)

  def __script_type_parser(self, js):
    for item in js:
      for it in item["Files"]:
        if it["File"] in self.__files:
          f = it["File"]
          it["File"] = str(pathlib.Path(self.__files[f]["Path"]).joinpath(f))
        
        it["Speed"] = float(it["Speed"])
        self.__list.append(it)

  def __random_type_parser(self, js):
    if len(self.__files) > 0:
      defaults = js["Default"]
      states = set()
      tags_js = js["Tags"]
      tags = dict()
      for t in tags_js:
        for tag in t["Tag"]:
          tags[tag] = {
            "Color" : t["Color"],
            "Size" : t["Size"],
            "Speed" : t["Speed"],
            "Length" : t["Length"],
            "Text" : t["Text"]
          }
      for item in self.__files:
        item = self.__files[item]
        for tag in tags:
          if tag in item["Tags"]:
            if tag not in states:
              states.add(tag)
              pass
            else:
              states.remove(tag)
              pass
        data = {
          "File" : str(pathlib.Path(self.__files[item]["Path"]).joinpath(item)), 
          "Length" : "", 
          "Text" : "", 
          "Color" : "", 
          "Size" : "", 
          "Speed" : ""
          }
        self.__list.append(data)


    random.shuffle(self.__list)