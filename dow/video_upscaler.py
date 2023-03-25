import pathlib
import cv2
import os
import sys
import shutil
import time

class VideoUpscaler():
  hw = {
    "cpu" : {
      "split" : "ffmpeg -i %s -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 %s/%s",
      "upscale" : "realesrgan-ncnn-vulkan -i %s -o %s -s 2 -j 5:10:10 -f png",
      "compile" : "ffmpeg -r %s -i %s/%s -i %s -map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -r %s -pix_fmt yuv420p %s",
      "convert" : "ffmpeg -vsync 0 -i %s %s"
    },
    "cuda" : {
      "split" : "ffmpeg -i %s -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 %s/%s",
      "upscale" : "realesrgan-ncnn-vulkan -n realesr-animevideov3 -i %s -o %s -s 3 -j 5:10:10 -f png",
      "compile" : "ffmpeg -r %s -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i %s/%s -i %s -map 0:v:0 -map 1:a:0? -c:a copy -c:v h264_nvenc -r %s -preset p4 -b:v 5M %s",
      "convert" : "ffmpeg -vsync 0 -i %s %s"
    },
    "mesa" : {
      "split" : "ffmpeg -hwaccel vaapi -i '%s' -qscale:v 1 -qmin 1 -qmax 1 %s/%s",
      "upscale" : "realesrgan-ncnn-vulkan -g 0,1 -i %s -o %s -s 2 -j 128:128:128,1:2:2 -f png", # 0 - discret, 1 - integrated, 2 - cpu
      "compile" : "ffmpeg -hwaccel vaapi -thread_queue_size 32 -i %s/%s -i '%s' -map 0:v:0 -map 1:a:0 -c:a copy -c:v hevc_vaapi -vf 'format=nv12,hwupload' '%s'",
      "convert" : "ffmpeg -hwaccel vaapi -i '%s' -c:v hevc_vaapi -vf 'format=nv12,hwupload' '%s'"
    }
  }
  # -vaapi_device /dev/dri/renderD128
  hw_used = "mesa"

  def __init__(self):
    self.tmp_dir = pathlib.Path.home().joinpath("tmp").joinpath("tmp_frames")
    self.tmp_dir.mkdir(exist_ok=True, parents=True)
    self.out_dir = pathlib.Path.home().joinpath("tmp").joinpath("out_frames")
    self.out_dir.mkdir(exist_ok=True, parents=True)

  def get_fps(self, filename_video):
    fps = 0
    cap=cv2.VideoCapture(str(filename_video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return str(fps)

  def __split(self, filename_video):
    os.system(self.hw[self.hw_used]["split"] % (str(filename_video), str(self.tmp_dir), f"frame%08d.png"))

  def __upscale(self):
    os.system(self.hw[self.hw_used]["upscale"] % (str(self.tmp_dir), str(self.out_dir)))

  def __compile(self, filename_video):
    name = filename_video.stem + ".mp4"
    out_file = self.out_dir.joinpath(name)
    fin_file = str(out_file).split(".")[0] + filename_video.suffix
    fin_file = pathlib.Path(fin_file)
    fps = self.get_fps(filename_video)
    st = time.perf_counter()
    os.system(self.hw[self.hw_used]["compile"] % (str(self.out_dir), f"frame%08d.png", str(filename_video), out_file))
    print(f"{time.perf_counter() - st}")
    if out_file.suffix != fin_file.suffix:
      os.system(self.hw[self.hw_used]["convert"] % (out_file, fin_file))
      if out_file.exists():
        out_file.unlink()
        out_file = fin_file
    if filename_video.exists():
      filename_video.unlink()
    shutil.move(out_file, filename_video)

  def __clean(self):
    shutil.rmtree(self.out_dir)
    shutil.rmtree(self.tmp_dir)

  def upscale(self, filename_video):
    filename_video = pathlib.Path(filename_video)
    self.__split(filename_video)
    self.__upscale()
    self.__compile(filename_video)
    self.__clean()

if __name__ == "__main__":
  f = VideoUpscaler()
  f.upscale(sys.argv[1])
