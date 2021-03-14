import pathlib
import sys
from classes.Config import DowConfig
from classes.Database import DowDatabase

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)
o = db.SelectAllFilesLike(sys.argv[1])

if o is not None:
  for f in o:
    print(f[:-1])
    print("\n")
else:
  print("None")


