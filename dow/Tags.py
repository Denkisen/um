import os

class DowTags():
  __tags_to_filter = []
  def __init__(self, tag_white_list_file_path):
    if os.path.exists(tag_white_list_file_path) and os.path.isfile(tag_white_list_file_path):
      f = open(tag_white_list_file_path)
      for line in f:
        self.__tags_to_filter.append(line)
      f.close()
  
  def FilterTags(self, tags):
    tags_list = []
    if tags is str:
      tags_list = tags.split(" ")
    elif tags is list:
      tags_list = tags

    ret_list = []
    for tag in tags_list:
      if tag in self.__tags_to_filter:
        ret_list.append(tag)
    if tags is str:
      return " ".join(ret_list)
    elif tags is list:
      return ret_list