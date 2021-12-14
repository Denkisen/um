import pathlib
from PySide6 import QtCore, QtWidgets, QtGui
from .Database import DowDatabase
from .Config import DowConfig
from .MimeType import DowMimeType

class ViewStruct():
  def __init__(self, widget : QtWidgets.QListView, model = None):
    self.widget = widget
    self.model = QtGui.QStandardItemModel() if model is None else model
    self.widget.setModel(self.model)

  def SetModel(self, model):
    self.model = model
    self.widget.setModel(self.model)

  def SetClickHandler(self, handler):
    self.widget.clicked[QtCore.QModelIndex].connect(handler)

  def SetDblClickHandler(self, handler):
    self.widget.doubleClicked[QtCore.QModelIndex].connect(handler)

class DowTagEditor():
  def __init__(self, all_tags : QtWidgets.QListView,
                     current_file_tags : QtWidgets.QListView,
                     files : QtWidgets.QListView,
                     next_button : QtWidgets.QPushButton,
                     back_button : QtWidgets.QPushButton,
                     save_button : QtWidgets.QPushButton,
                     search_box : QtWidgets.QLineEdit):
    self.__db = None
    self.__config = None
    self.__all_tags = None
    self.__image_change_event_handler = None
    self.current_file = ""

    self.__all_tags_widget = ViewStruct(all_tags)
    self.__all_tags_widget.SetDblClickHandler(self.__all_tags_widget_double_click)
    self.__all_tags_widget.widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    a = QtGui.QAction("Get Files with tag", self.__all_tags_widget.widget)
    a.triggered.connect(self.__select_files_with_tag)
    self.__all_tags_widget.widget.addAction(a)

    self.__selected_tags_widget = ViewStruct(current_file_tags)
    self.__files_widget = ViewStruct(files)
    self.__files_widget.SetClickHandler(self.__files_widget_click)
    self.__files_widget.widget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    a = QtGui.QAction("Delete", self.__files_widget.widget)
    a.triggered.connect(self.__delete_action)
    self.__files_widget.widget.addAction(a)

    self.__next_button = next_button
    self.__back_button = back_button
    self.__save_button = save_button
    self.__search_box = search_box
    self.__next_button.clicked.connect(self.__next_button_click)
    self.__back_button.clicked.connect(self.__back_button_click)
    self.__save_button.clicked.connect(self.__save_button_click)
    self.__search_box.textChanged.connect(self.__search_box_changed)
    QtGui.QImageReader.setAllocationLimit(256)
    pass

  def keyPressEvent(self, event : QtGui.QKeyEvent):
    if event.key() == QtCore.Qt.Key_Left:
      self.__back_button.clicked.emit()

    if event.key() == QtCore.Qt.Key_Right:
      self.__next_button.clicked.emit()

    if event.key() == QtCore.Qt.Key_Return:
      self.__save_button.clicked.emit()
      self.__next_button.clicked.emit()

  @QtCore.Slot()
  def __delete_action(self):
    if self.__files_widget.model.rowCount() > 0 and self.__config != None:
      index = self.__files_widget.widget.currentIndex()
      f = pathlib.Path(self.__files_widget.model.itemFromIndex(index).text())

      pathlib.Path(self.__config.ROOT_DIR).joinpath("ToDelete").mkdir(parents=True, exist_ok=True)
      f.rename(pathlib.Path(self.__config.ROOT_DIR).joinpath("ToDelete").joinpath(f.name))
      print(f"delete: {self.__files_widget.model.itemFromIndex(index).text()}")
      self.__files_widget.model.removeRow(index)
      self.__next_button.clicked.emit()

  @QtCore.Slot()
  def __next_button_click(self):
    index = self.__files_widget.widget.currentIndex()
    if index.row() == self.__files_widget.model.rowCount() - 1:
      index = self.__files_widget.model.index(0, 0)
    else:
      index = self.__files_widget.model.index(index.row() + 1, 0)

    self.__files_widget_click(index)

  @QtCore.Slot()
  def __back_button_click(self):
    index = self.__files_widget.widget.currentIndex()
    if index.row() == 0:
      index = self.__files_widget.model.index(self.__files_widget.model.rowCount() - 1, 0)
    else:
      index = self.__files_widget.model.index(index.row() - 1, 0)

    self.__files_widget_click(index)

  @QtCore.Slot()
  def __save_button_click(self):
    if self.__files_widget.model.rowCount() > 0:
      index = self.__files_widget.widget.currentIndex()
      f = pathlib.Path(self.__files_widget.model.itemFromIndex(index).text())
      tags = []
      for l in self.__selected_tags_widget.model.findItems("", QtCore.Qt.MatchRegularExpression):
        if l.checkState() == QtCore.Qt.Checked:
          tags.append(l.text())

      tags = " ".join(tags)
      if self.__db is not None:
        self.__db.Update(f.name, "tags", tags)

  @QtCore.Slot()
  def __search_box_changed(self):
    model = QtGui.QStandardItemModel()
    text = self.__search_box.text().lower()
    if self.__search_box.text() != "":
      for s in self.__all_tags:
        if text in s.lower():
          item = QtGui.QStandardItem(s)
          item.setCheckable(False)
          item.setEditable(False)
          model.appendRow(item)
    else:
      model = self.__all_tags_model
    self.__all_tags_widget.SetModel(model)

  @QtCore.Slot()
  def __all_tags_widget_double_click(self, index):
    item = QtGui.QStandardItem(self.__all_tags_widget.model.itemFromIndex(index))
    item.setCheckable(True)
    item.setCheckState(QtCore.Qt.CheckState.Checked)
    if len(self.__selected_tags_widget.model.findItems(item.text(), QtCore.Qt.MatchExactly)) == 0:
      self.__selected_tags_widget.model.appendRow(item)
      self.__selected_tags_widget.widget.scrollToBottom()

  @QtCore.Slot()
  def __files_widget_click(self, index):
    self.__files_widget.widget.selectionModel().clear()
    self.__files_widget.widget.selectionModel().setCurrentIndex(index, QtCore.QItemSelectionModel.SelectCurrent)
    self.__selected_tags_widget.model.clear()
    item = self.__files_widget.model.itemFromIndex(index)
    self.current_file = item.text()
    if self.__image_change_event_handler is not None:
      self.__image_change_event_handler()

    if self.__db is not None:
      f = self.__db.SelectFile(pathlib.Path(self.current_file).name)
      if f is not None:
        tgs = f[2].split(" ")
        for t in tgs:
          item = self.__all_tags_model.findItems(t, QtCore.Qt.MatchExactly)
          if len(item) > 0:
            item = QtGui.QStandardItem(item[0])
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)
            self.__selected_tags_widget.model.appendRow(item)

  @QtCore.Slot()
  def __select_files_with_tag(self):
    index = self.__all_tags_widget.widget.selectedIndexes()
    if len(index) > 0:
      index = index[0]
      if self.__db is not None:
        self.ClearFiles()
        from_db = self.__db.SelectFilesWith("tags", self.__all_tags_widget.model.itemFromIndex(index).text())
        files = []
        for f in from_db:
          if self.__all_tags_widget.model.itemFromIndex(index).text() in str(f[2]).split(" "):
            files.append(pathlib.Path(f[1], f[0]))
        self.AddFiles(files)

  def SetConfig(self, conf : DowConfig):
    self.__config = conf

  def SetDatabase(self, db : DowDatabase):
    self.__db = db
    self.__all_tags = set()
    tags = self.__db.Execute("SELECT tags FROM files")
    for line in tags:
      line = str(line[0]).split(" ")
      for l in line:
        self.__all_tags.add(l)
    
    self.__all_tags_model = QtGui.QStandardItemModel()
    for t in self.__all_tags:
      item = QtGui.QStandardItem(t)
      item.setCheckable(False)
      item.setEditable(False)
      self.__all_tags_model.appendRow(item)

    self.__search_box_changed()

  def ClearFiles(self):
    self.__files_widget.model.clear()
    self.current_file = ""
    self.__selected_tags_widget.model.clear()
    self.__image_change_event_handler()

  def AddFiles(self, files : list):
    select = None
    for f in files:
      f = pathlib.Path(f)
      if f.suffix in DowMimeType("").all_formats_suffix_list:
        item = QtGui.QStandardItem(str(f))
        item.setCheckable(False)
        item.setEditable(False)
        if select is None:
          select = item
        self.__files_widget.model.appendRow(item)

    ind = self.__files_widget.model.indexFromItem(select)
    self.__files_widget_click(ind)
    self.__files_widget.widget.scrollTo(ind)

  def ImageChangeEvent(self, handler):
    self.__image_change_event_handler = handler
