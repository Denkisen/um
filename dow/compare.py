import sys
import pathlib
import threading
from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGL
from classes import DowMimeType
from classes import DowGlImage
from classes import DowConfig

class MainWidget(QtWidgets.QWidget):
  def __init__(self, app):
    super().__init__()
    self.__config = DowConfig(pathlib.Path(".").joinpath("config.json"))
    self.__app = app
    self.__files = []
    self.__iterator = 0
    self.__selected_left = True
    self.__gl_mutex = threading.Lock()

    self.__main_layout = QtWidgets.QVBoxLayout()
    self.__images_layout = QtWidgets.QHBoxLayout()
    self.__left_image_layout = QtWidgets.QVBoxLayout()

    self.__left_image_widget = QtWidgets.QWidget()
    self.__left_image_widget_layout = QtWidgets.QGridLayout(self.__left_image_widget)
    self.__left_image_widget_layout.setContentsMargins(1,1,1,1)
    self.__left_image_widget.setStyleSheet("background-color: yellow")
    
    self.__left_image = DowGlImage(self.__left_image_widget)
    self.__left_image_widget_layout.addWidget(self.__left_image)

    self.__left_image_info = QtWidgets.QLabel("")
    self.__left_image_info.setFixedHeight(30)
    self.__left_image_layout.addWidget(self.__left_image_widget)
    self.__left_image_layout.addWidget(self.__left_image_info)

    self.__right_image_layout = QtWidgets.QVBoxLayout()

    self.__right_image_widget = QtWidgets.QWidget()
    self.__right_image_widget_layout = QtWidgets.QGridLayout(self.__right_image_widget)
    self.__right_image_widget_layout.setContentsMargins(1,1,1,1)

    self.__right_image = DowGlImage(self.__right_image_widget)
    self.__right_image_widget_layout.addWidget(self.__right_image)

    self.__right_image_info = QtWidgets.QLabel("")
    self.__right_image_info.setFixedHeight(30)
    self.__right_image_layout.addWidget(self.__right_image_widget)
    self.__right_image_layout.addWidget(self.__right_image_info)
    self.__buttons_layout = QtWidgets.QHBoxLayout()
    self.__open_button = QtWidgets.QPushButton("Open")
    self.__open_button.clicked.connect(self.__open_button_click)
    self.__next_button = QtWidgets.QPushButton("Next")
    self.__next_button.clicked.connect(self.__next_button_click)
    self.__update_button = QtWidgets.QPushButton("Update")
    self.__update_button.clicked.connect(self.__update_button_click)
    self.__buttons_layout.addWidget(self.__open_button)
    self.__buttons_layout.addWidget(self.__next_button)
    self.__buttons_layout.addWidget(self.__update_button)

    self.__images_layout.addLayout(self.__left_image_layout)
    self.__images_layout.addLayout(self.__right_image_layout)
    self.__main_layout.addLayout(self.__images_layout)
    self.__main_layout.addLayout(self.__buttons_layout)
    self.setLayout(self.__main_layout)

    self.__app.installEventFilter(self)

  def __set_image(self, filename, left : bool):
    x, y = DowMimeType(filename).GetSize()
    filename = pathlib.Path(filename)
    if left:
      self.__left_image.SetImage(str(filename))
      self.__left_image_info.setText(f"{filename.name}    {x}x{y}")
      self.__left_image.update()
    else:
      self.__right_image.SetImage(str(filename))
      self.__right_image_info.setText(f"{filename.name}    {x}x{y}")
      self.__right_image.update()

  def __clear_image(self, left : bool):
    if left:
      self.__left_image.Clear()
      self.__left_image_info.setText("")
      self.__left_image.update()
    else:
      self.__right_image.Clear()
      self.__right_image_info.setText("")
      self.__right_image.update()

  def __delete_selected(self):
    index = 0
    if self.__selected_left:
      index = 0
    else:
      index = 1
    
    pathlib.Path(self.__config.ROOT_DIR).joinpath("ToDelete").mkdir(parents=True, exist_ok=True)
    f = pathlib.Path(self.__files[self.__iterator][index])
    f.rename(pathlib.Path(self.__config.ROOT_DIR).joinpath("ToDelete").joinpath(f.name))
    print(f"delete: {self.__files[self.__iterator][index]}")
    self.__next_button.clicked.emit()

  @QtCore.Slot()
  def __update_button_click(self):
    self.__left_image.update()
    self.__right_image.update()

  @QtCore.Slot()
  def __next_button_click(self):
    print("Next")
    while self.__iterator < len(self.__files):
      self.__iterator += 1
      if self.__iterator < len(self.__files):
        if pathlib.Path(self.__files[self.__iterator][0]).exists() and pathlib.Path(self.__files[self.__iterator][1]).exists():
          self.__set_image(self.__files[self.__iterator][0], True)
          self.__set_image(self.__files[self.__iterator][1], False)
          break
      else:
        self.__files.clear()
        self.__iterator = 0
        self.__clear_image(True)
        self.__clear_image(False)
        break


  @QtCore.Slot()
  def __open_button_click(self):
    files = QtWidgets.QFileDialog.getOpenFileName(self, 
                "Open File", 
                str(pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.DUPS)), 
                "Dups file (*.txt)"
                )
    self.__files.clear()
    self.__iterator = 0

    f = pathlib.Path(files[0])
    if files[0] != "" and f.exists():
      f = f.open("r")
      for line in f:
        if ' | ' in line:
          sp = line.replace("\n","").split(' | ')
          if len(sp) == 2:
            f1 = pathlib.Path(sp[0])
            f2 = pathlib.Path(sp[1])
            if f1.exists() and f2.exists() and f1.suffix in DowMimeType("").image_formats_suffix_list and f2.suffix in DowMimeType("").image_formats_suffix_list:
              self.__files.append([sp[0], sp[1]])

    if len(self.__files) > 0:
      self.__set_image(self.__files[self.__iterator][0], True)
      self.__set_image(self.__files[self.__iterator][1], False)
    else:
      self.__clear_image(True)
      self.__clear_image(False)

  def keyPressEvent(self, event : QtGui.QKeyEvent):
    super(MainWidget, self).keyPressEvent(event)
    
    if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Right:
      self.__selected_left = not self.__selected_left

      if self.__selected_left:
        self.__left_image_widget.setStyleSheet("background-color: yellow")
        self.__right_image_widget.setStyleSheet("background-color: black")
      else:
        self.__right_image_widget.setStyleSheet("background-color: yellow")
        self.__left_image_widget.setStyleSheet("background-color: black")
    elif event.key() == QtCore.Qt.Key_Return:
      self.__next_button_click()
    elif event.key() == QtCore.Qt.Key_Delete:
      self.__delete_selected()

  def eventFilter(self, object, event):
    if type(event) == QtGui.QKeyEvent and (event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Right):
      self.keyPressEvent(event)
      return True
    else:
      return False

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  widget = MainWidget(app)
  widget.resize(1280, 720)
  widget.show()

  sys.exit(app.exec_())