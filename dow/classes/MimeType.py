import magic
import cv2
import pathlib

class DowMimeType():
  image_formats_suffix_list = set(['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'])
  video_formats_suffix_list = set(['.mp4', '.gif', '.webm', '.ts'])
  all_formats_suffix_list = image_formats_suffix_list.union(video_formats_suffix_list)
  def __init__(self, file):
    self.__file = str(file)

  def GetType(self):
    return str(magic.from_file(self.__file, mime=True)).split("/")[-1]

  def GetSize(self):
    f = cv2.imread(str(self.__file), cv2.IMREAD_UNCHANGED)
    return f.shape[1], f.shape[0]
