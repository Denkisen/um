import os
import shutil
import pathlib
from ffpyplayer.player import MediaPlayer
import cv2
import time
from ImageUpscaler import ImageUpscaler

file_name = pathlib.Path("/run/media/marko/nice6/um/ToAdd/9808177_hq.mp4")
tmp_dir = pathlib.Path("/tmp/output")
tmp_dir.mkdir(parents=True, exist_ok=True)

video = cv2.VideoCapture(str(file_name))
fps = video.get(cv2.CAP_PROP_FPS)
res_video = None
engine = ImageUpscaler(tmp_dir)

index = 0
while video.isOpened():
  ret, frame = video.read()
  if ret:
    save_image_name = file_name.name + f".{index}.png"
    save_image_path = tmp_dir.joinpath(save_image_name)
    cv2.imwrite(str(save_image_path), frame)

    #upscale
    engine.exec(save_image_path,scale=3)
    time.sleep(0.01)
    #
    frame = cv2.imread(str(save_image_path))
    if res_video == None:
      height, width, layers = frame.shape
      o = tmp_dir.joinpath(file_name.name + ".mp4")
      res_video = cv2.VideoWriter(str(o), cv2.VideoWriter.fourcc('M','J','P','G'), fps, (width,height))
    res_video.write(frame)
    save_image_path.unlink()

  
  index += 1
