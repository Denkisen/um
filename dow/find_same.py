from classes.Config import DowConfig
from classes.Database import DowDatabase
import pathlib
import tensorflow as tf
import numpy as np
from sklearn.neighbors import NearestNeighbors

class Features():
  def __init__(self):
    self.__log = pathlib.Path("./log.txt").open("w")
    self.__config = DowConfig(pathlib.Path(".").joinpath("config.json"))
    self.__db = DowDatabase(self.__config.ROOT_DIR, self.__config.DB_NAME)
    self.__model = tf.keras.applications.VGG19(weights='imagenet', include_top=False)
    self.__files, self.__features = self.__load_files()
    self.__knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
    self.__knn.fit(self.__features)

  def __del__(self):
    self.__log.close()

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
      if f.suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        db_res = self.__db.SelectFile(f.name)
        if db_res is None:
          self.__move_to_error(f)
        elif db_res[3] == "no":
          try:
            fts = self.get_features(f)
            st = ' '.join(str(x) for x in fts)
            self.__db.Update(f.name, "features", st)
            files.append(f)
            features.append(fts)
          except:
            self.__move_to_error(f)
        else:
          ts = np.array(list(map(np.float32, db_res[3].split(' '))))
          files.append(f)
          features.append(ts)
    return files, features

  def find_dups(self):
    dups = pathlib.Path(self.__config.ROOT_DIR).joinpath(self.__config.DUPS).open("w")
    for i in range(len(self.__files)):
      dist, indices = self.__knn.kneighbors(self.__features[i].reshape(1, -1), n_neighbors=5)
      for j in indices[0]:
        if self.__files[j] == self.__files[i]:
          continue
        elif dist[0][list(indices[0]).index(j)] < 0.3:
          dups.write("%s | %s\n" % (self.__files[j], self.__files[i]))
    dups.close()


if __name__ == '__main__':
  f = Features()
  f.find_dups()