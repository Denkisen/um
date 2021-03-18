from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
import pathlib

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)

def files_diff():
  files_db = set()
  files_glob = set()

  for t in db.SelectAll():
    files_db.add(pathlib.Path(t[1]).joinpath(t[0]))

  for t in pathlib.Path(config.ROOT_DIR).glob("**/*"):
    if t.suffix in DowMimeType("").image_formats_suffix_list:
      files_glob.add(t)

  inter = files_glob.difference(files_db)
  print(inter)

def files_format():
  for t in pathlib.Path(config.ROOT_DIR).glob("**/*.*"):
    db_file = db.SelectFileLike(t.stem)
    if db_file is not None:
      true_ext = DowMimeType(t).GetType()
      if true_ext is None:
        if t.suffix in DowMimeType("").image_formats_suffix_list:
          folder = pathlib.Path(config.ROOT_DIR).joinpath(config.ERROR_FOLDER)
          folder.mkdir(parents=True, exist_ok=True)
          t.replace(folder.joinpath(t.name))
          print("Error : " + str(t))
          db.Update(db_file[0], "path", folder)
        continue

      true_ext = ".jpg" if true_ext == "jpeg" else "." + true_ext
      if t.suffix != true_ext or pathlib.Path(db_file[0]).suffix != true_ext or t.suffix != pathlib.Path(db_file[0]).suffix:
        new_name = pathlib.Path(t.stem + true_ext)
        print(f"Old name: {t}, New name: {new_name}")
        t.replace(new_name)
        db.Update(db_file[0], "name", new_name.name)

files_format()