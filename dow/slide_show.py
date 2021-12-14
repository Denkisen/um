import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from classes import DowConfig
from classes import DowDatabase
from classes import DowSlideShowManager

class MainWidget(QtWidgets.QWidget):
  def __init__(self, app):
    super().__init__()
    self.__app = app
    self.__config = DowConfig(pathlib.Path(".").joinpath("config.json"))
    self.__db = None
    if pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.DB_NAME).exists():
      self.__db = DowDatabase(self.__config.ROOT_DIR, self.__config.DB_NAME)
    else:
      print("No db")

    self.setLayout(QtWidgets.QVBoxLayout())
    self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
    self.__slide_manager = DowSlideShowManager(self.__config, self.__db, pathlib.Path("slide_script_1.json"), "1.wav", self.__OnSlideEnd)
    self.layout().addWidget(self.__slide_manager)

  @QtCore.Slot()
  def __OnSlideEnd(self):
    exit(0)

  def keyPressEvent(self, event : QtGui.QKeyEvent):
    super(MainWidget, self).keyPressEvent(event)
    if event.key() == QtCore.Qt.Key_Space:
      pass
    else:
      exit(0)

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  widget = MainWidget(app)
  widget.resize(800, 800)
  widget.showFullScreen()
  widget.show()

  sys.exit(app.exec())