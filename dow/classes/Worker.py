
class DowWorker():
  def __init__(self):
    pass

  def Worker(self, module, db, file_in_db_func, file_no_in_db_func):
    while module.GetNextPage():
      for i in range(module.GetFilesLen()):
        file = module.GetFile(i)
        if file is None:
          return

        short_name = module.GetShortFileName(file)
        if db.IsFileInLike(short_name):
          if file_in_db_func is not None and not file_in_db_func(module, file):
            print("End of worker")
            return
        else:
          if file_no_in_db_func is not None and not file_no_in_db_func(module, file):
            print("End of worker")
            return

    