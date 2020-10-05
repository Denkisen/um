import pygame
from PIL import Image
from PIL import ImageTk

class SImage():
  def __init__(self, screen):
    self.scr = screen

  def Draw(self, file_name):
    raw_img = Image.open(file_name)
    w, h = pygame.display.get_surface().get_size()
    rate = min(w / raw_img.size[0], h / raw_img.size[1])
    raw_img = raw_img.resize((round (raw_img.size[0] * rate), round (raw_img.size[1] * rate)), Image.ANTIALIAS)
    surface = pygame.image.fromstring(raw_img.tobytes(), raw_img.size, raw_img.mode)
    self.scr.blit(surface.convert(), [(w - raw_img.size[0]) // 2, (h - raw_img.size[1]) // 2])