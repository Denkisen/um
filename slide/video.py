import pyglet
import pygame
import time
import ctypes
from text import SText

class SVideo(pyglet.window.Window):
  def __init__(self, screen):
    w, h = pygame.display.get_surface().get_size()
    super(SVideo, self).__init__(w, h, fullscreen = False, visible=False)
    self.player = pyglet.media.Player()
    self.scr = screen
    self.loop = False
    self.current_file = ""
    self.text = ""
    self.textDraw = SText(self.scr)

  def Play(self, file, text = ""):
    self.current_file = file
    self.player = pyglet.media.Player()
    self.player.volume = 0
    self.player.queue(pyglet.media.load(file))
    self.player.play()
    self.text = text

  def SetScreen(self, screen):
    self.scr = screen

  def Loop(self, enable):
    self.loop = enable

  def on_draw(self):
    if self.player.source is not None:
      rawimage = self.player.get_texture().get_image_data()
      pixels = rawimage.get_data('RGBA', rawimage.width * 4)
      w, h = pygame.display.get_surface().get_size()
      video = pygame.image.frombuffer(pixels, (rawimage.width, rawimage.height), 'RGBA')
      rate = min(w / rawimage.width, h / rawimage.height)
      picture = pygame.transform.scale(video, (round (rawimage.width * rate), round (rawimage.height * rate)))
      self.scr.blit(picture, [(w - round (rawimage.width * rate)) // 2, (h - round (rawimage.height * rate)) // 2])
      self.textDraw.Draw(self.text)

  def IsPlaying(self):
    return self.player.playing

  def Tick(self):
    pyglet.clock.tick()

    if self.player.source is not None:
      if self.player.source.duration <= self.player.time:
        if self.loop:
          self.player.seek(0.0)
        else:
          self.player.pause()
    else:
      if not self.player.playing and self.loop and self.current_file is not "":
        self.Play(self.current_file)
    

    for self.window in pyglet.app.windows:
      self.window.switch_to()
      self.window.dispatch_events()
      self.window.dispatch_event('on_draw')
  

