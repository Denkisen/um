from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
import pathlib

def reset_path():
  __config = DowConfig(pathlib.Path(".").joinpath("config.json"))
  __db = DowDatabase(__config.ROOT_DIR, __config.DB_NAME)
  files = []
  new_path = pathlib.Path(__config.ROOT_DIR).joinpath(__config.DOWNLOAD_FOLDER)
  for f in new_path.glob("**/*"):
    if f.suffix in DowMimeType("").image_formats_suffix_list:
      db_res = __db.SelectFile(f.name)
      if not db_res is None:
        __db.Update(f.name, 'path', str(new_path))
      else:
        print(f"Error: {f.name}")

if __name__ == '__main__':
  reset_path()