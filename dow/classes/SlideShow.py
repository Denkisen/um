import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
import json
from ffpyplayer.player import MediaPlayer
from classes import DowConfig
from classes import DowDatabase
from classes import DowGlImage
from .SequenceScriptParser import DowSequenceScriptParser

class DowSlideShowManager(QtWidgets.QWidget):
  def __init__(self, config : DowConfig, db : DowDatabase, script : pathlib.Path, beat_sound : str, onSlideEndCallback):
    QtWidgets.QWidget.__init__(self)
    self.__config = config
    self.__db = db
    self.__onSlideEndCallback = onSlideEndCallback
    script_type = json.loads(script.read_text())["Type"]
    self.__image = DowGlImage()
    self.__image.setContentsMargins(0, 0, 0, 0)

    self.__text = QtWidgets.QLabel(parent=self.__image)
    
    self.setLayout(QtWidgets.QVBoxLayout())
    self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
    self.layout().addWidget(self.__image)
    self.__sound = MediaPlayer(beat_sound)
    self.__sound.set_pause(True)
    self.__sound.set_volume(1.0)

    if script_type == "Sequence":
      self.__engine = DowSequenceScriptParser(script, db, self.__config)
      self.__engine.setTextSignal.connect(self.__SetText)
      self.__engine.setTextAttributesSignal.connect(self.__SetTextAttributes)
      self.__engine.setTextPositionSignal.connect(self.__SetTextPosition)
      self.__engine.setImageSignal.connect(self.__SetImage)
      self.__engine.setVideoSignal.connect(self.__SetVideo)
      self.__engine.onSlideShowEnd.connect(self.__onSlideEndCallback)
      self.__engine.setImageListSignal.connect(self.__SetImageList)
      self.__engine.nextFileInImageList.connect(self.__NextFileInList)
      self.__engine.playSound = self.__PlayBeatSound
      self.__engine.Run()

  @QtCore.Slot(str,str)
  def __SetTextAttributes(self, color : str, size : str):
    self.__text.setStyleSheet("QLabel { color : %s; font-size : %s; }" % (color, size))
    self.__text.adjustSize()

  @QtCore.Slot(QtCore.QPoint)
  def __SetTextPosition(self, pos : QtCore.QPoint):
    self.__text.move(QtCore.QPoint(self.width() * (pos.x() / 100), self.height() * (pos.y() / 100)))

  @QtCore.Slot(str)
  def __SetText(self, text : str):
    self.__text.setText(text)
    self.__text.adjustSize()

  @QtCore.Slot()
  def __PlayBeatSound(self):
    self.__sound.seek(0, relative=False)
    self.__sound.set_pause(False)

  @QtCore.Slot(str)
  def __SetImage(self, file : str):
    self.__image.SetImage(file)

  @QtCore.Slot(list)
  def __SetImageList(self, files : list):
    self.__image.SetImageList(files)

  @QtCore.Slot(str)
  def __SetVideo(self, file : str):
    self.__image.SetVideo(file)

  @QtCore.Slot()
  def __NextFileInList(self):
    self.__image.NextFromList()
