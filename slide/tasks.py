import sqlite3
import json
import os
import random

class STasks:
  def __init__(self, dir):
    self.dir = dir
    self.iter = 0
    self.files = []
    self.state_list = []
    self.config_name = "config.conf"
    self.GetAllFiles(dir)
    random.shuffle(self.files)
    self.Test()
    
  def GetAllFiles(self, dir):
    self.files = []
    for root, directories, filenames in os.walk(dir):
      for filename in filenames:
        if str.lower(os.path.splitext(filename)[-1]) in ['.bmp', '.jpg', '.png', '.gif', '.webm', '.mp4']: 
          self.files.append(os.path.join(root, filename))

  def Test(self):
    ret = []
    vid = 5
    img = 5
    for f in self.files:
      ext = f.split(".")[-1]
      if ext in ['webm', 'mp4']:
        if vid > 1:
          ret.append(f)
          vid -= 1
      else:
        if img > 1:
          ret.append(f)
          img -= 1
    self.files = ret
  def GetTask(self, file_path):
    ret = ""
    f = open(os.path.join(self.dir, self.config_name), "r")
    for line in f:
      spt = line.split(':')
      sub = spt[0].split(',')
      for s in sub:
        if s in file_path:
          if spt[0] in self.state_list:
            self.state_list.remove(spt[0])
            ret = spt[2]
          else:
            self.state_list.append(spt[0])
            ret = spt[1]
    f.close()
    return ret

  def GetNext(self):
    if self.iter < len (self.files) - 1:
      self.iter += 1
    else:
      self.iter = 0
      random.shuffle(self.files)

    return [self.files[self.iter], self.GetTask(self.files[self.iter])]

