import magic
import pathlib

class DowMimeType():
  all_formats_suffix_list = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.mp4', '.gif', '.webm']
  image_formats_suffix_list = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
  video_formats_suffix_list = ['.mp4', '.gif', '.webm']
  def __init__(self, file):
    self.__file = str(file)

  def GetType(self):
    return str(magic.from_file(self.__file, mime=True)).split("/")[-1]