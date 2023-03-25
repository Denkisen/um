import os
from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
from classes.ImageUpscaler import ImageUpscaler
import pathlib
import shutil
from PIL import Image

MIN_W = 1920
MIN_H = 1080

def check_file(file_path):
  global MIN_W
  global MIN_H

  image = Image.open(str(file_path))
  res = 0
  w, h = image.size
  if w < MIN_W or h < MIN_H:
    res = 2

  return res

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME, False)

files = db.SelectAll()
engine = ImageUpscaler(pathlib.Path("/tmp"))

for i, file in enumerate(files):
  path = pathlib.Path(file[1]).joinpath(file[0])
  if path.exists() and path.suffix in DowMimeType.image_formats_suffix_list:
    res = check_file(path)
    if res > 0:
      print(f"Upscale image: {str(path)}")
      engine.exec(path, scale=res)