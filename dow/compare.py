import pathlib
import os
from classes.Config import DowConfig
from classes.Database import DowDatabase

config = DowConfig(pathlib.Path(".").joinpath("config.json"))

for file in pathlib.Path(config.ROOT_DIR).joinpath(config.DUPS).open("r"):
  first, second = file.split(" | ", 2)
  if pathlib.Path(first).exists() and pathlib.Path(second[:-1]).exists():
    os.system("gwenview \"%s\" | gwenview \"%s\"" % (first, second[:-1]))