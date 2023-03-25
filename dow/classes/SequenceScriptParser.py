import json
import pathlib
import threading
import time
import random
import datetime
import copy
from PySide6 import QtCore, QtWidgets, QtGui
from .Database import DowDatabase
from .MimeType import DowMimeType
from .Config import DowConfig

class DowSequenceScriptParserSignals(QtCore.QObject):
  setTextSignal = QtCore.Signal(str)
  setTextAttributesSignal = QtCore.Signal(str,str)
  setTextPositionSignal = QtCore.Signal(QtCore.QPoint)
  onSlideShowEnd = QtCore.Signal()
  setImageSignal = QtCore.Signal(str)
  setImageListSignal = QtCore.Signal(list)
  setVideoSignal = QtCore.Signal(str)
  nextFileInImageList = QtCore.Signal()

class DowSequenceScriptParser(DowSequenceScriptParserSignals):
  def __init__(self, script_file : pathlib.Path, db : DowDatabase, config : DowConfig):
    DowSequenceScriptParserSignals.__init__(self)
    self.__running = True
    self.playSound = None

    self.__script = json.loads(script_file.read_text())
    self.__files = []
    self.__db = db
    self.__config = config
    self.__audio_speed = 0.0
    self.__index = 0
    self.__Parse()

    self.__main_audio_loop_task = threading.Thread(target=self.__audio_loop, args=(), daemon=True)
    self.__main_visual_loop_task = threading.Thread(target=self.__visual_loop, args=(), daemon=True)
    
  def Run(self):
    self.__main_visual_loop_task.start()
    self.__main_audio_loop_task.start()

  def __Parse(self):
    if self.__script["Type"] != "Sequence":
      print("Invalid script type")
      return

    if self.__script["Version"] != 1.0:
      print("Unsoported version")
      return

    for page in self.__script["Pages"]:

      fs = self.__GetFiles(page["File"], page["ImageCount"])
      time = (datetime.datetime.strptime(page["Time"], "%H:%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()
      time /= page["ImageCount"]
      for f in fs:
        p = copy.copy(page)
        p["File"] = f
        p["Time"] = time

        self.__files.append(p)

  def __add_file_if_image(self, file, file_list):
    if file.suffix in DowMimeType("").all_formats_suffix_list:
      file_list.add(str(file))
      return True
    else:
      return False

  def __GetFiles(self, file_list : list, count : int):
    files = set()
    res_files = []

    for f in file_list:
      p = pathlib.Path(f)

      if f == "*":
        records = self.__db.SelectAll()
        if len(records) > 0:
          min_one = False
          for r in records:
            p = pathlib.Path(r[1]).joinpath(r[0])
            if p.exists():
              files.add(str(p))
              min_one = True

          if min_one:
            continue

      if p.exists():
        #File Path
        if p.is_file() and self.__add_file_if_image(p, files):
          continue
        #Folder Path
        if p.is_dir():
          for d in p.iterdir():
            tf = p.joinpath(d)
            self.__add_file_if_image(tf, files)

          continue
  
      #Folder
      p = pathlib.Path(self.__config.ROOT_DIR).joinpath(f)
      if p.exists() and p.is_dir():
        for d in p.iterdir():
          tf = p.joinpath(d)
          self.__add_file_if_image(tf, files)

        continue

      #File Name
      records = self.__db.SelectAllFilesLike(f)
      if len(records) > 0:
        for r in records:
          p = pathlib.Path(r[1]).joinpath(r[0])
          if p.exists(): files.add(str(p))

        continue
      #Tag
      sql = f"SELECT name, path, tags FROM files WHERE tags Like '%{f}%'"
      records = self.__db.Execute(sql)
      if len(records) > 0:
        min_one = False
        for r in records:
          p = pathlib.Path(r[1]).joinpath(r[0])
          if f in str(r[2]).split(" ") and p.exists():
            files.add(str(p))
            min_one = True

        if min_one:
          continue

    if len(files) > 0:
      max_len = min(count, len(files))
      while len(res_files) < max_len:
        fs = random.sample(list(files), 1)
        pa = pathlib.Path(fs[0])
        if not pa in res_files:
          res_files.append(pa)

    return res_files

  def __del__(self):
    self.__running = False

  def __audio_loop(self):
    while self.__running:
      if self.__audio_speed <= 0.01:
        time.sleep(1)
      else:
        if callable(self.playSound):
          self.playSound()
        time.sleep(60.0 / self.__audio_speed)

  def __visual_loop(self):
    while self.__running:
      interval = 0.1
      if self.__index >= len(self.__files):
        self.onSlideShowEnd.emit()
        break

      item = self.__files[self.__index]
      #SetFile
      filename = item["File"]
      if filename.suffix in DowMimeType("").image_formats_suffix_list:
        self.setImageSignal.emit(str(filename))
      elif filename.suffix in DowMimeType("").video_formats_suffix_list:
        self.setVideoSignal.emit(str(filename))
      #TextSettings
      p = item["Text"]["ShiftFromLeftUpCorner"]
      self.setTextPositionSignal.emit(QtCore.QPoint(p[0], p[1]))
      self.setTextAttributesSignal.emit(item["Text"]["Color"], item["Text"]["Size"])
      self.setTextSignal.emit(item["Text"]["Value"])
      #Audio
      self.__audio_speed = item["Beat"]["Bpm"]
      #Interval
      interval = item["Time"]
      self.__index += 1
      time.sleep(interval)
    
