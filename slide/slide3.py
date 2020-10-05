from pydub import AudioSegment
from pydub.playback import play
from PIL import Image
from PIL import ImageTk
import sqlite3
import json
import os
import time
import threading
import random
import pygame
import pyglet
from tasks import STasks
from video import SVideo
from image import SImage
from text import SText
from audio import SAudio


DB_PATH = ""
SLIDE_CONFIG = ""
state_list = []

f = open("config.json", "r")
conf = json.load(f)
SLIDE_CONFIG = conf["SLIDE_CONFIG"]
DB_PATH = conf["DB_PATH"]
f.close()
  

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
pygame.init()

screen = pygame.display.set_mode((1920, 1035), pygame.NOFRAME)#
video = SVideo(screen)
tasks = STasks(DB_PATH)
image = SImage(screen)
text = SText(screen)
beep = SAudio("1.wav")
clock = pygame.time.Clock()

running = True
pause = False
video_playing = False
flip_timer = 0
timeout = 2

beep.PlayInLoop()

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        pause = not pause
        video.Loop(pause)
        beep.NoChange(pause)
      else:
        running = False

  if video_playing and not video.IsPlaying():
    video_playing = False

  if not pause and not video_playing:
    now = time.time()
    if flip_timer == 0 or now - flip_timer >= timeout:
      flip_timer = now

      screen.fill(0)

      task = tasks.GetNext()
      ext = task[0].split('.')[-1]
      if ext not in ['webm', 'mp4']:
        image.Draw(task[0])
        text.Draw(task[1])
      else:
        video.Play(task[0])
        video_playing = True

  video.Tick()
  pygame.display.update()
  pygame.display.flip()
  clock.tick(60)

beep.Stop()