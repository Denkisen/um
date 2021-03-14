from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
import pathlib

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)
add_folder = pathlib.Path(config.ROOT_DIR, config.ADD_FOLDER)

for file in add_folder.glob("**/*"):
  if file.suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.mp4', '.gif', '.webm']:
    if not db.IsFileIn(file.name):
      db.Insert(file.name, file.parents[0], "tagme")

