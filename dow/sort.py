from classes.Config import DowConfig
from classes.Database import DowDatabase
import pathlib

conf = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(conf.ROOT_DIR, conf.DB_NAME)
tagdict = dict()

for line in pathlib.Path(conf.ROOT_DIR).joinpath(conf.MAP_NAME).open("r"):
  if ':' in line:
    folder, tags_list = line.split(":", 1)
    tagdict[folder] = set(tags_list.replace("\n", "").split(","))

for row in db.SelectAll():
  name, path, tags, features = row
  source = pathlib.Path(path).joinpath(name)

  if not source.exists():
    db.Delete(name)
    continue
  else:
    tags = set(tags.replace("\n", "").split(" "))
    found = False
    for line in tagdict:
      if tagdict[line].intersection(tags):
        dest = pathlib.Path(conf.ROOT_DIR).joinpath(line)
        dest.mkdir(parents=True, exist_ok=True)
        if dest.joinpath(name) != source:
          source.replace(dest.joinpath(name))
          print(f"Move {source} to {dest}")
          db.Update(name, "path", dest)
        found = True
        break
    
    if not found:
      dest = pathlib.Path(conf.ROOT_DIR).joinpath(conf.UNSORTED_FOLDER)
      dest.mkdir(parents=True, exist_ok=True)
      if dest.joinpath(name) != source:
        source.replace(dest.joinpath(name))
        db.Update(name, "path", dest)




