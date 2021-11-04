import pathlib
from PySide6 import QtCore, QtWidgets, QtGui, QtOpenGLWidgets, QtOpenGL
import cv2
from ffpyplayer.player import MediaPlayer
import numpy as np
from OpenGL import GL as pygl
from shiboken6 import VoidPtr

class DowGlImage(QtOpenGLWidgets.QOpenGLWidget):
  __data = np.array([-1.0, -1.0, 0.0,  0.0, 0.0,
                      -1.0, 1.0, 0.0,  0.0, 1.0,
                      1.0, 1.0, 0.0,  1.0, 1.0,
                      1.0, -1.0, 0.0,  1.0, 0.0],
                    dtype=np.float32)

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

  def __init__(self, parent = None):
    QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
    self.context = QtGui.QOpenGLContext()
    self.__type_size = np.float32().nbytes
    self.__null_ptr = VoidPtr(0)
    self.__vertex_size_ptr = VoidPtr(3 * self.__type_size)
    self.__texture_generator = None
    self.__player = None
    self.__is_video = False

  def __CreateShader(self, shader_type, source):
    shader = QtOpenGL.QOpenGLShader(shader_type)
    if not shader.compileSourceCode(source):
      print(shader.log())
      return None

    return shader

  def __CreateBuffer(self, buff_type : QtOpenGL.QOpenGLBuffer.Type, size : int):
    buffer = QtOpenGL.QOpenGLBuffer(buff_type)
    buffer.create()
    buffer.bind()
    buffer.allocate(self.__null_ptr, size)
    buffer.release()
    return buffer

  def __CreateTexture(self, image):
    texture = QtOpenGL.QOpenGLTexture(QtOpenGL.QOpenGLTexture.Target2D)
    texture.setMinMagFilters(QtOpenGL.QOpenGLTexture.Filter.Nearest, QtOpenGL.QOpenGLTexture.Filter.Linear)
    texture.setBorderColor(0, 0, 0, 1)
    texture.setWrapMode(QtOpenGL.QOpenGLTexture.ClampToBorder)
    texture.setAutoMipMapGenerationEnabled(False)
    texture.DontGenerateMipMaps = True
    texture.setData(QtGui.QImage(image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGBA8888).mirrored())
    return texture

  def __DrawUpdate(self):
    self.update()
    pass

  def __image_stream(self, filename):
    image = cv2.imread(str(filename), cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    tex = self.__CreateTexture(image)
    if self.__player is not None:
      self.__player.close_player()
      self.__player = None

    while True:
      yield tex

  def __video_stream(self, filename):
    video = cv2.VideoCapture(str(filename))
    if self.__player is not None:
      self.__player.close_player()
      self.__player = None

    self.__player = MediaPlayer(str(filename))
    self.__player.set_pause(True)
    self.__player.set_volume(1.0)
    
    self._is_video_playing = True
    fps = video.get(cv2.CAP_PROP_FPS)
    if fps > 0:
      self.__draw_timer.setInterval(1000 / fps)
    else:
      self.__draw_timer.setInterval(1000 / 30)

    while video.isOpened():
      ret, frame = video.read()
      
      self.__player.get_frame(show=False)
      if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        tex = self.__CreateTexture(frame)
        self.__player.set_pause(False)
        yield tex
      else:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.__player.seek(0, relative=False)
    
    self._is_video_playing = False
    self.__draw_timer.setInterval(1000 / 30)
    return None

  @QtCore.Slot(str)
  def SetImage(self, filename : str):
    self.__is_video = False
    # if self.__texture_generator != None:
    #   tex = next(self.__texture_generator)
    #   tex.destroy()
    self.__texture_generator = self.__image_stream(filename)

  @QtCore.Slot(str)
  def SetVideo(self, filename):
    self._is_video = True
    self.__texture_generator = self.__video_stream(filename)

  def Clear(self):
    self.__texture_generator = None

  def initializeGL(self):
    self.context.create()
    self.context.aboutToBeDestroyed.connect(self.cleanUpGl)

    funcs = self.context.functions()
    funcs.initializeOpenGLFunctions()
    funcs.glClearColor(0, 0, 0, 1)

    self.__mesh_buffer = self.__CreateBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer, self.__data.size * self.__type_size)
    self.__mesh_buffer.bind()
    self.__mesh_buffer.write(0, self.__data.tobytes(), self.__data.size * self.__type_size)
    self.__mesh_buffer.release()
    
    self.__program = QtOpenGL.QOpenGLShaderProgram(self.context)
    self.__program.addShader(self.__CreateShader(QtOpenGL.QOpenGLShader.Vertex, self.__vertex_shader))
    self.__program.addShader(self.__CreateShader(QtOpenGL.QOpenGLShader.Fragment, self.__frag_shader))
    self.__program.link()

    self.__uniform_tex_bias = self.__program.uniformLocation("biasTexCoord")

    self.__vao = QtOpenGL.QOpenGLVertexArrayObject(self.context)
    self.__vao.create()

    self.__vao.bind()
    self.__mesh_buffer.bind()

    funcs.glVertexAttribPointer(0, 3, int(pygl.GL_FLOAT), int(pygl.GL_FALSE), 5 * self.__type_size, self.__null_ptr)
    funcs.glVertexAttribPointer(1, 2, int(pygl.GL_FLOAT), int(pygl.GL_FALSE), 5 * self.__type_size, self.__vertex_size_ptr)

    funcs.glEnableVertexAttribArray(0)
    funcs.glEnableVertexAttribArray(1)

    self.__mesh_buffer.release()
    self.__vao.release()

    self.__draw_timer = QtCore.QTimer()
    self.__draw_timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
    self.__draw_timer.timeout.connect(self.__DrawUpdate)
    self.__draw_timer.start(1000 / 30)

  def resizeGL(self, w, h):
    funcs = self.context.functions()
    funcs.glViewport(0, 0, w, h)
    pass

  def paintGL(self):
    funcs = self.context.functions()
    funcs.glClear(pygl.GL_COLOR_BUFFER_BIT)

    if self.__texture_generator != None:
      texture = None
      try:
        texture = next(self.__texture_generator)
      except:
        pass

      if texture != None:
        self.__program.bind()

        rate = min(self.size().width() / texture.width(), self.size().height() / texture.height())
        rate_x = (texture.width() / self.size().width()) * rate
        rate_y = (texture.height() / self.size().height()) * rate

        if self.__uniform_tex_bias > -1:
          self.__program.setUniformValue(self.__uniform_tex_bias, rate_x, rate_y)

        self.__vao.bind()
        funcs.glActiveTexture(pygl.GL_TEXTURE0)
        texture.bind()

        funcs.glDrawArrays(int(pygl.GL_POLYGON), 0, 4)

        texture.release()
        self.__vao.release()
        self.__program.release()
        if self.__is_video:
          texture.destroy()
      else:
        self.__texture_generator = None
        self.__is_video = False

  def cleanUpGl(self):
    self.context.makeCurrent(self.context.surface())
    self.__mesh_buffer.destroy()
    self.__vao.destroy()
    del self.__program
    self.__program = None
    self.context.doneCurrent()
    pass

class MainWindow(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.widget1 = DowGlImage(self)
    self.widget2 = DowGlImage(self)
    self.button = QtWidgets.QPushButton("Test")
    self.button.clicked.connect(self.__click)
    mainLayout = QtWidgets.QHBoxLayout()
    mainLayout.addWidget(self.widget1)
    mainLayout.addWidget(self.widget2)
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