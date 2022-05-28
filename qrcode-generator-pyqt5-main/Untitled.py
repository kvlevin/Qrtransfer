import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QOpenGLVersionProfile
from PyQt5.QtWidgets import (QApplication, QWidget, QOpenGLWidget, QHBoxLayout)
 
class MyGLWidget(QOpenGLWidget):
   
    def __init__(self, parent=None):
        super(MyGLWidget, self).__init__(parent)
       
    def initializeGL(self):
        version_profile = QOpenGLVersionProfile()
        version_profile.setVersion(2, 0)
        self.gl = self.context().versionFunctions(version_profile)
        self.gl.initializeOpenGLFunctions()
       
        #设置背景色
        self.gl.glClearColor(0.9,0.9,0.9, 1.0)
        #深度测试
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
       
    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
         
        #self.gl.glRotated(30.0, 1.0, 0.0, 0.0)      
        self.gl.glBegin(self.gl.GL_TRIANGLES)
            # self.gl.glBegin(self.gl.GL_TRIANGLES)
        self.gl.glColor3d(1.0, 0.0, 0.0)

        self.gl.glVertex3d(1.0, 1.0, 0.0)
            
        self.gl.glColor3d(1.0, 0.0, 0.0)

        self.gl.glVertex3d(1.0, -1.0, 0.0)

        self.gl.glColor3d(0.0, 1.0, 0.0)

        self.gl.glVertex3d(-1.0, -1.0, 0.0)

        # self.gl.glColor3d(0.0, 0.0, 1.0)

        # self.gl.glVertex3d(1.0, -1.0, 0.0)


        self.gl.glEnd()







       
    def resizeGL(self, width, height):
 
        side = min(width, height)
        if side < 0:
            return
           
        #视口
        self.gl.glViewport((width - side) // 2, (height - side) // 2, side, side)
        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        #正交投射
        self.gl.glOrtho(-1.5, 1.5, -1.5, 1.5, -10, 10)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)
 
