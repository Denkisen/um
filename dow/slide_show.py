import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
from classes.GlImage import DowGlImage
from classes.SlideShow import DowSlideShow

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

    self.__slide_view = DowGlImage(self)
    self.__slide_label = QtWidgets.QLabel("Test")
    self.__slide_label.setFixedHeight(30)

    self.__slide_label.setStyleSheet("QLabel { color : blue; font-size : 32px; }")
    self.__slide_layout = QtWidgets.QVBoxLayout()
    self.__slide_space = QtWidgets.QWidget()
    self.__slide_layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
    self.__slide_layout.addWidget(self.__slide_label)
    self.__slide_layout.addWidget(self.__slide_space)
    
    self.__slide_layout.setAlignment(self.__slide_label, QtCore.Qt.AlignHCenter)
    self.__slide_view.setLayout(self.__slide_layout)
    main_layout = QtWidgets.QVBoxLayout()
    main_layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
    main_layout.addWidget(self.__slide_view)
    self.setLayout(main_layout)
    self.__engine = DowSlideShow(self.__config, self.__db, pathlib.Path("~/Projects/py-scripts/um/dow/random_slide_script.json"), self.__slide_view, self.__slide_label)

  def keyPressEvent(self, event : QtGui.QKeyEvent):
    super(MainWidget, self).keyPressEvent(event)
    if event.key() == QtCore.Qt.Key_Space:
      pass
    else:
      exit(0)

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  widget = MainWidget(app)
  widget.resize(1280, 720)
  #widget.showFullScreen()
  widget.show()

  sys.exit(app.exec_())