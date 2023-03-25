import os
import pathlib
import shutil
from PIL import Image

class ImageUpscaler():
  def __init__(self, tmp_dir):
    self.__tmp_path = pathlib.Path(tmp_dir)

  def exec(self, input_path, output_path = None, scale = 2):
    if not scale in [2,3,4]:
      return False

    tmp_out_path = self.__tmp_path.joinpath(pathlib.Path(input_path).name)
    os.system(f"realesrgan-ncnn-vulkan -i '{str(input_path)}' -o '{str(tmp_out_path)}' -s {scale}")
    if tmp_out_path.exists():
      path = input_path
      if output_path != None: path = output_path

      shutil.move(tmp_out_path, path)
      return True
    else:
      return False
