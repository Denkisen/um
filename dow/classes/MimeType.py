import magic
import pathlib

class DowMimeType():
  def __init__(self, file):
    self.__file = str(file)

  def GetType(self):
    return str(magic.from_file(self.__file, mime=True)).split("/")[-1]