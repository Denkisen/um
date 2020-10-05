from pydub import AudioSegment
from pydub.playback import play
import time
import threading
import random

class SAudio():
  def __init__(self, file):
    self.ref_file = AudioSegment.from_wav(file)
    self.p_file = self.ref_file
    self.SpeedChange(5.0)
    self.stop = False
    self.no_change = False
    self.pause = False
    self.interval = 1.0
    self.counter = 0
    self.max = 120
    self.speed_range = [
        [0.1, 120], 
        [0.35, 120], 
        [0.5, 120], 
        [0.75, 120], 
        [1.0, 120]]
    self.beep_thread = None

  def Stop(self):
    self.stop = True
  
  def NoChange(self, state):
    self.no_change = state

  def Pause(self, state):
    self.pause = state

  def Loop(self):
    if not self.pause and not self.no_change:
      self.counter += 1
      if self.counter >= self.max:
        self.interval, self.max = random.choice(self.speed_range)
        self.counter = 0

    if not self.pause:
      play(self.p_file)

    if not self.stop:
      threading.Timer(self.interval, self.Loop).start()

  def PlayInLoop(self):
    self.stop = False
    self.beep_thread = threading.Thread(target=self.Loop, args=())
    self.beep_thread.start()

  def SpeedChange(self, speed=1.0):
    sound_with_altered_frame_rate = self.ref_file._spawn(self.ref_file.raw_data, overrides={
      "frame_rate": int(self.ref_file.frame_rate * speed)
    })
    self.p_file = sound_with_altered_frame_rate.set_frame_rate(self.ref_file.frame_rate)
    