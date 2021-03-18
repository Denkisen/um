import sys
import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from classes.TagEditor import DowTagEditor
from classes.Config import DowConfig
from classes.Database import DowDatabase

class MainWidget(QtWidgets.QMainWindow):
  def __init__(self, app):
    super().__init__()
    self.__app = app
    self.__config = DowConfig(pathlib.Path(".").joinpath("config.json"))
    #Controls
    ## Menu Bar
    self.__file_menu = QtWidgets.QMenu("File")
    self.__file_menu.addAction("Open Files", self.__show_open_files_dialog)
    self.__file_menu.addAction("Open Directory", self.__show_open_dir_dialog)
    self.__file_menu.addAction("Clear Files", self.__clear_files)
    self.__file_menu.addAction("Close", self.__close)

    self.__menu_bar = QtWidgets.QMenuBar()
    self.__menu_bar.addMenu(self.__file_menu)
    self.setMenuBar(self.__menu_bar)
    ## Left side
    self.__image = QtWidgets.QLabel()
    self.__image.setAlignment(QtCore.Qt.AlignVCenter)

    self.__controls_left_layout = QtWidgets.QVBoxLayout()
    self.__left_box = QtWidgets.QWidget()
    self.__left_box_layout = QtWidgets.QVBoxLayout(self.__left_box)

    self.__left_box_layout.addWidget(self.__image)
    self.__controls_left_layout.addWidget(self.__left_box)
    ## Right side
    self.__search_box = QtWidgets.QLineEdit()
    self.__all_tags = QtWidgets.QListView()
    self.__all_tags.setMaximumHeight(150)

    self.__selected_tags = QtWidgets.QListView()
    self.__files = QtWidgets.QListView()
    self.__files.setMinimumHeight(200)
    self.__files.setMaximumHeight(200)

    self.__back_button = QtWidgets.QPushButton("Back")
    self.__next_button = QtWidgets.QPushButton("Next")
    self.__save_button = QtWidgets.QPushButton("Save")

    self.__buttons_right_layout = QtWidgets.QHBoxLayout()
    self.__buttons_right_layout.addWidget(self.__back_button)
    self.__buttons_right_layout.addWidget(self.__next_button)
    self.__buttons_right_layout.addWidget(self.__save_button)

    self.__right_box = QtWidgets.QWidget()
    self.__right_box.setMinimumWidth(200)
    self.__right_box.setMaximumWidth(300)

    self.__controls_right_layout = QtWidgets.QVBoxLayout(self.__right_box)
    self.__controls_right_layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
    self.__controls_right_layout.addWidget(self.__search_box)
    self.__controls_right_layout.addWidget(self.__all_tags)
    self.__controls_right_layout.addWidget(self.__selected_tags)
    self.__controls_right_layout.addWidget(self.__files)
    self.__controls_right_layout.addLayout(self.__buttons_right_layout)

    #Layouts
    self.__main_widget = QtWidgets.QWidget()
    
    self.__main_layout = QtWidgets.QHBoxLayout(self.__main_widget)
    self.__main_layout.addLayout(self.__controls_left_layout)
    self.__main_layout.addWidget(self.__right_box)
    self.setCentralWidget(self.__main_widget)

    #Logic
    self.__logic = DowTagEditor(self.__all_tags, 
                                self.__selected_tags,
                                self.__files,
                                self.__next_button,
                                self.__back_button,
                                self.__save_button,
                                self.__search_box)
    if pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.DB_NAME).exists():
      self.__db = DowDatabase(self.__config.ROOT_DIR, self.__config.DB_NAME)
      self.__logic.SetDatabase(self.__db)
      self.__logic.ImageChangeEvent(self.__load_image)

  @QtCore.Slot()
  def __show_open_files_dialog(self):
    files = QtWidgets.QFileDialog.getOpenFileNames(self, 
                "Open Files", 
                self.__config.ROOT_DIR, 
                "Images (*.png *.jpeg *.jpg *.bmp *.tiff)"
                )
    self.__logic.AddFiles(files[0])

  @QtCore.Slot()
  def __show_open_dir_dialog(self):
    dirs = QtWidgets.QFileDialog.getExistingDirectory(self, 
                "Open Directory",
                self.__config.ROOT_DIR,
                QtWidgets.QFileDialog.ShowDirsOnly | 
                QtWidgets.QFileDialog.DontResolveSymlinks)
    files = list(pathlib.Path(dirs).glob("**/*.*"))
    self.__logic.AddFiles(files)

  @QtCore.Slot()
  def __clear_files(self):
    self.__logic.ClearFiles()

  @QtCore.Slot()
  def __close(self):
    exit(0)

  @QtCore.Slot()
  def __load_image(self):
    file_path = pathlib.Path(self.__logic.current_file)
    if file_path.name != "" and file_path.exists():
      pix = QtGui.QPixmap(str(file_path))
      s = self.__left_box.size()
      s.setHeight(s.height() - 20)
      pix = pix.scaled(s, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation) # scaledToWidth(self.__left_box.size().width() - 20, QtCore.Qt.TransformationMode.SmoothTransformation)
      self.__image.setPixmap(pix)
    else:
      self.__image.clear()

  @QtCore.Slot()
  def resizeEvent(self, event: QtGui.QResizeEvent):
    self.__load_image()
    pass

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  widget = MainWidget(app)
  widget.resize(800, 600)
  widget.show()

  sys.exit(app.exec_())