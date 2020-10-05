import pygame

class SText():
  def __init__(self, screen):
    self.scr = screen

  def Draw(self, text):
    font = pygame.font.Font(pygame.font.get_default_font(), 50) 
    text = font.render(text, True, (0, 0, 128), (0,0,0))
    textRect = text.get_rect() 
    textRect.center = ((textRect.width // 2) + 50, (textRect.height // 2) + 50)  
    self.scr.blit(text, textRect) 