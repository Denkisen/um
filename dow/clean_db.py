import pathlib
from classes.Config import DowConfig
from classes.Database import DowDatabase

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)

files = db.SelectAll()

if files is None or len(files) == 0:
  exit(0)

for line in files:
  name, path, tags, features = line
  if not pathlib.Path(path).joinpath(name).exists():
    db.Delete(name)