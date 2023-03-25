import imagehash
from PIL import Image
import pathlib
import numpy as np

class PercHash():
  __HASH_SIZE = 16
  def __init__(self):
    pass

  def calculate(self, image_path : pathlib.Path):
    return imagehash.phash(Image.open(str(image_path)), hash_size=self.__HASH_SIZE)

  def calculate_to_flatten(self, image_path : pathlib.Path):
    return self.calculate(image_path).hash.flatten()

  def from_flatten(self, data):
    m = np.array(data, dtype=np.bool8).reshape((self.__HASH_SIZE,self.__HASH_SIZE))
    return imagehash.ImageHash(m)