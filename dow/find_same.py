from classes.Config import DowConfig
from classes.Database import DowDatabase
from classes.MimeType import DowMimeType
import pathlib
import tensorflow as tf
import numpy as np
from sklearn.neighbors import NearestNeighbors
import time
from multiprocessing import Process
from multiprocessing import Manager
from multiprocessing.managers import SharedMemoryManager
import sys

class Features():
  def __init__(self):
    self.__log = pathlib.Path("./log.txt").open("w")
    self.__config = DowConfig(pathlib.Path(".").joinpath("config.json"))
    self.__db = DowDatabase(self.__config.ROOT_DIR, self.__config.DB_NAME)
    self.__model = tf.keras.applications.VGG19(weights='imagenet', include_top=False)
    self.shm_manager = SharedMemoryManager()
    self.shm_manager.start()
    start = time.perf_counter()
    self.__files, self.__features = self.__load_files()
    print(f"Load files: {time.perf_counter() - start}")
    self.__knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
    start = time.perf_counter()
    self.__knn.fit(self.__features)
    print(f"Fit: {time.perf_counter() - start}")
    print(sys.getsizeof(self.__files))
    print(sys.getsizeof(self.__features))
    print(sys.getsizeof(self.__knn))
    self.manager = Manager()
    self.dups_dict = self.manager.dict()

  def __del__(self):
    self.__log.close()
    self.shm_manager.shutdown()

  def __load_image(self, file_name):
    img = tf.keras.preprocessing.image.load_img(str(file_name), target_size=(224, 224))
    x = tf.keras.preprocessing.image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    return tf.keras.applications.vgg19.preprocess_input(x)

  def __move_to_error(self, file):
    self.__log.write(str(file) + "\n")
    self.__log.flush()
    folder = pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.ERROR_FOLDER)
    folder.mkdir(parents=True, exist_ok=True)
    file.replace(folder.joinpath(file.name))
    print("Error : " + str(file))

  def get_features(self, file_name):
    return self.__model.predict(self.__load_image(file_name)).ravel()
  
  def __load_files(self):
    files = []
    features = []
    for f in pathlib.Path(self.__config.ROOT_DIR).glob("**/*"):
      if f.suffix in DowMimeType("").image_formats_suffix_list:
        db_res = self.__db.SelectFile(f.name)
        if db_res is None:
          self.__move_to_error(f)
        elif db_res[3] == "no":
          try:
            fts = self.get_features(f)
            st = ' '.join(str(x) for x in fts)
            self.__db.Update(f.name, "features", st)
            files.append(str(f))
            features.append(fts)
          except:
            self.__move_to_error(f)
        else:
          ts = np.array(list(map(np.float32, db_res[3].split(' '))))
          files.append(str(f))
          features.append(ts)
    return self.shm_manager.ShareableList(files), features

  def worker(start, end, core, features, files, knn, dups_dict):
    l = []
    y = 0
    for i in range(start, end):
      f = features[y].reshape(1, -1)
      y += 1
      dist, indices = knn.kneighbors(f, n_neighbors=5)
      for j in indices[0]:
        if files[j] == files[i]:
          continue
        elif dist[0][list(indices[0]).index(j)] < 0.4:
          l.append("%s | %s\n" % (files[j], files[i]))

    dups_dict[core] = l

  def find_dups(self):
    dups = pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.DUPS).open("w")
    self.dups_dict.clear()
    procs = []
    cores = 16
    files_num = 400 # len(self.__files)
    arr_len = int(files_num / cores)
    start = 0
    for core in range(cores):
      end = start + arr_len if core != cores - 1 else files_num - 1
      procs.append(Process(target=Features.worker, args=(start, end, core, self.__features[start:end], self.__files, self.__knn, self.dups_dict,)))
      procs[-1].start()
      start = end + 1

    for proc in procs:
      proc.join()

    for a in self.dups_dict:
      dups.writelines(self.dups_dict[a])

    dups.close()


if __name__ == '__main__':
  f = Features()
  y = time.perf_counter()
  start = time.perf_counter()
  f.find_dups()
  print(f"Find Dups: {time.perf_counter() - start}")
  print(time.perf_counter() - y)
