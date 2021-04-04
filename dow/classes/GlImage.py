import pathlib
from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGL, QtOpenGLWidgets
from PySide6.QtGui import QOpenGLFunctions as GL
import ctypes
import numpy as np
from shiboken6 import VoidPtr
from OpenGL import GL as pygl
import threading
import time
import cv2
from ffpyplayer.player import MediaPlayer

class DowGlImage(QtOpenGLWidgets.QOpenGLWidget, QtGui.QOpenGLFunctions):
  __vertex_shader = """
    #version 440 core
    layout(location = 0) in vec3 inPosition;
    layout(location = 1) in vec2 texCoord;
    layout(location = 2) uniform vec2 biasTexCoord;

    layout(location = 0) out vec3 outColor;
    layout(location = 1) out vec2 outCoord;

    void main()
    {
      outColor = vec3(1.0f, 0.5f, 1.0f);
      outCoord = texCoord;
      float pos_x = inPosition.x * biasTexCoord.x;
      float pos_y = inPosition.y * biasTexCoord.y;

      gl_Position = vec4(pos_x, pos_y, 0.0, 1.0);
    }"""
  
  __frag_shader = """
    #version 440 core
    layout(location = 0) in vec3 inColor;
    layout(location = 1) in vec2 texCoord;
    layout(location = 0) out vec4 outColor;
    uniform sampler2D inTexture;

    void main()
    {
      outColor = texture(inTexture, texCoord);
    }
    """
  def __init__(self, parent):
    QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
    GL.__init__(self)
    self.__data = np.array(
      [-1.0, -1.0, 0.0,  0.0, 0.0,
        -1.0, 1.0, 0.0,  0.0, 1.0,
        1.0, 1.0, 0.0,  1.0, 1.0,
        1.0, -1.0, 0.0,  1.0, 0.0],
      dtype=ctypes.c_float)
      
    self._is_video = False
    self._is_video_playing = False

    self.__video_thread = threading.Thread(target=self.__video_play, args=(), daemon=True)
    self.__video_thread.start()
    self.__texture_generator = None
    self.__player = None
    self.__uniform_tex_bias = -1

  def __del__(self):
    self.__video_thread._stop()
    self.__video_thread.join()

  def initializeGL(self):
    self.initializeOpenGLFunctions()
    self.glClearColor(0, 0, 0, 1)

    self.__program = QtOpenGL.QOpenGLShaderProgram()
    self.__program.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Vertex, self.__vertex_shader)
    self.__program.addShaderFromSourceCode(QtOpenGL.QOpenGLShader.Fragment, self.__frag_shader)
    self.__program.link()
    
    self.__uniform_tex_bias = self.__program.uniformLocation("biasTexCoord")

    self.__vao = QtOpenGL.QOpenGLVertexArrayObject()
    self.__vao.create()
    self.__vao.bind()

    self.__buffer = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
    self.__buffer.create()
    self.__buffer.bind()

    float_size = ctypes.sizeof(ctypes.c_float)
    null = VoidPtr(0)
    pointer = VoidPtr(3 * float_size)
    
    self.__buffer.allocate(self.__data.tobytes(), self.__data.size * float_size)
    self.glVertexAttribPointer(0, 3, int(pygl.GL_FLOAT), int(pygl.GL_FALSE), 5 * float_size, null)
    self.glVertexAttribPointer(1, 2, int(pygl.GL_FLOAT), int(pygl.GL_FALSE), 5 * float_size, pointer)
    self.glEnableVertexAttribArray(0)
    self.glEnableVertexAttribArray(1)
    self.__vao.release()
    self.__buffer.release()

  def resizeGL(self, w, h):
    self.makeCurrent()
    self.glViewport(0, 0, w, h)

  def paintGL(self):
    self.makeCurrent()
    self.glClear(pygl.GL_COLOR_BUFFER_BIT)

    if self.__texture_generator is not None:
      texture = None
      try:
        texture = next(self.__texture_generator)
      except:
        pass

      if texture is not None:
        rate = min(self.size().width() / texture.width(), self.size().height() / texture.height())
        rate_x = (texture.width() / self.size().width()) * rate
        rate_y = (texture.height() / self.size().height()) * rate
        self.__program.bind()
        if self.__uniform_tex_bias > -1:
          self.__program.setUniformValue(self.__uniform_tex_bias, rate_x, rate_y)

        self.__vao.bind()
        self.glActiveTexture(pygl.GL_TEXTURE0)
        texture.bind()
        self.glDrawArrays(int(pygl.GL_POLYGON), 0, 4)
        self.__program.release()
        if self._is_video:
          texture.destroy()
      else:
        self.__texture_generator = None
        self._is_video = False

  def __create_texture(self, image):
    texture = QtOpenGL.QOpenGLTexture(QtOpenGL.QOpenGLTexture.Target2D)
    texture.setMinMagFilters(QtOpenGL.QOpenGLTexture.Filter.Nearest, QtOpenGL.QOpenGLTexture.Filter.Linear)
    texture.setBorderColor(0, 0, 0, 1)
    texture.setWrapMode(QtOpenGL.QOpenGLTexture.ClampToBorder)
    texture.setAutoMipMapGenerationEnabled(False)
    texture.DontGenerateMipMaps = True
    texture.setData(QtGui.QImage(image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGBA8888).mirrored())
    return texture

  def __video_stream(self, filename):
    video = cv2.VideoCapture(str(filename))
    if self.__player is not None:
      self.__player.close_player()
      self.__player = None

    self.__player = MediaPlayer(str(filename))
    self.__player.set_volume(1.0)
    self._is_video_playing = True
    while video.isOpened():
      ret, frame = video.read()
      self.__player.get_frame(show=False)
      if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        tex = self.__create_texture(frame)
        yield tex
      else:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.__player.seek(0, relative=False)
    
    self._is_video_playing = False
    return None

  def __image_stream(self, filename):
    image = cv2.imread(str(filename), cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    tex = self.__create_texture(image)
    if self.__player is not None:
      self.__player.close_player()
      self.__player = None

    while True:
      yield tex

  def SetImage(self, filename):
    self._is_video = False
    self.__texture_generator = self.__image_stream(filename)

  def SetVideo(self, filename):
    self._is_video = True
    self.__texture_generator = self.__video_stream(filename)

  def Clear(self):
    self.__texture_generator = None

  def __video_play(self):
    while True:
      try:
        self.update()
      except:
        break
      time.sleep(0.0416)

class MainWindow(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.widget = DowGlImage(self)
    self.button = QtWidgets.QPushButton("Test")
    self.button.clicked.connect(self.__click)
    mainLayout = QtWidgets.QVBoxLayout()
    mainLayout.addWidget(self.widget)
    mainLayout.addWidget(self.button)
    self.setLayout(mainLayout)

  @QtCore.Slot()
  def __click(self):
    pass

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    widget = MainWindow()
    widget.resize(800, 720)
    widget.show()
    app.exec_()