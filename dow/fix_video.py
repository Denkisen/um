from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.Sankaku2 import DowSankaku
from classes.Pixiv import DowPixiv
from classes.Worker import DowWorker
from classes.MimeType import DowMimeType
import pathlib
from multiprocessing import Process

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME)
download_dir = pathlib.Path(config.ROOT_DIR).joinpath(config.DOWNLOAD_FOLDER)
sankaku = DowSankaku(config.SAN_USER, config.SAN_PASSWORD, download_dir, config.SAN_USER_TAG + "+~webm+~mp4")
pixiv = DowPixiv(download_dir, config.PIXIV_TOKEN)

procs = []

if not sankaku.IsConnected():
  exit(1)

def check_file_type(file):
  file = pathlib.Path(file)
  img_type = DowMimeType(file).GetType()
  img_type = "jpg" if img_type == "jpeg" else img_type
  if img_type != None and img_type != file.suffix:
    img_type = "." + img_type
    new_file = pathlib.Path(str(file).split(".")[0] + img_type)
    return new_file
  else:
    return file

def download_file(module, file):
  global db
  global download_dir
  short_name = module.GetShortFileName(file)
  if module.DownloadFile(file):
    if len(file[1]) > 1:
      for f in file[1]:
        f = pathlib.Path(f)
        p = download_dir.joinpath(short_name)
        new_name = check_file_type(p.joinpath(f))
        if new_name.suffix != f.suffix:
          p.joinpath(f).replace(new_name)

        print("Insert to db: %s" % new_name)
        db.Insert(new_name.name, p, file[2])
    else:
      f = pathlib.Path(file[1][0])
      new_name = check_file_type(download_dir.joinpath(f)) if f.suffix not in ['.mp4', '.gif', '.webm'] else download_dir.joinpath(f)
      if new_name.suffix != f.suffix:
        download_dir.joinpath(f).replace(new_name)

      print("Insert to db: %s" % new_name)
      db.Insert(new_name.name, download_dir, file[2])

def file_in_db(module, file):
  global db
  global config
  for f in file[1]:
    f = pathlib.Path(f)
    if f.suffix in ['.mp4', '.gif', '.webm']:
      dbf = db.SelectAllFilesLike(f.name)
      if dbf is None:
        download_file(module, file)
      else:
        for df in dbf:
          real = pathlib.Path(df[1]).joinpath(df[0])
          if real.exists():
            new = pathlib.Path(df[1]).joinpath(f.name)
            if new.name != real.name:
              real.replace(new)
              print(f"Update {df[0]} to {new.name}")
              db.Update(df[0], "name", new.name)
          else:
            gl = pathlib.Path(config.ROOT_DIR).glob(f"**/{f.stem}")
            something_in = False
            for gf in gl:
              something_in = True
              new_folder = gf.parents[0]
              new_name = f.name
              print(f"Update {df} to {new_folder}, {new_name}")
              db.Update(df[0], "path", new_folder)
              db.Update(df[0], "name", new_name)
            
            if not something_in:
              download_file(module, file)
      
  return True

download_worker = DowWorker()
procs.append(Process(target=download_worker.Worker, args=(sankaku, db, file_in_db, file_in_db,)))
procs.append(Process(target=download_worker.Worker, args=(pixiv, db, file_in_db, file_in_db,)))
procs[0].start()
procs[1].start()
for proc in procs:
  proc.join()