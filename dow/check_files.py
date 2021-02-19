from Config import DowConfig
from Database import DowDatabase
import pathlib

config = DowConfig()
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)

files_db = set()
files_glob = set()

for t in db.SelectAll():
  files_db.add(pathlib.Path(t[1]).joinpath(t[0]))

for t in pathlib.Path(config.ROOT_DIR).glob("**/*"):
  if t.suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
    files_glob.add(t)

inter = files_glob.difference(files_db)
print(inter)

