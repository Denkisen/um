from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.Sankaku import DowSankaku
from classes.Pixiv import DowPixiv
from classes.Worker import DowWorker
from classes.MimeType import DowMimeType
import pathlib
from multiprocessing import Process

config = DowConfig(pathlib.Path(".").joinpath("config.json"))
db = DowDatabase(config.ROOT_DIR, config.DB_NAME, False)
download_dir = pathlib.Path(config.ROOT_DIR).joinpath(config.DOWNLOAD_FOLDER)
sankaku = DowSankaku(config.SAN_USER, config.SAN_PASSWORD, download_dir, config.SAN_USER_TAG)
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
      new_name = check_file_type(download_dir.joinpath(f)) if f.suffix not in DowMimeType("").video_formats_suffix_list else download_dir.joinpath(f)
      if new_name.suffix != f.suffix:
        download_dir.joinpath(f).replace(new_name)

      print("Insert to db: %s" % new_name)
      db.Insert(new_name.name, download_dir, file[2])

p_skip_state = False
def p_file_in_db(module, file):
  global db
  global p_skip_state
  name = module.GetShortFileName(file)
  if name == "99301793":
   p_skip_state = False
   return True

  return p_skip_state

s_skip_state = False
def s_file_in_db(module, file):
  global db
  global s_skip_state
  name = module.GetShortFileName(file)
  if name == "5122f15b93c1c8a8187b4f9a3984eef":
    s_skip_state = False
    return True

  return s_skip_state

def file_no_in_db(module, file):
  download_file(module, file)

  return True

procs.append(Process(target=DowWorker().Worker, args=(sankaku, db, s_file_in_db, file_no_in_db,)))
procs.append(Process(target=DowWorker().Worker, args=(pixiv, db, p_file_in_db, file_no_in_db,)))
for proc in procs:
  proc.start()

for proc in procs:
  proc.join()
