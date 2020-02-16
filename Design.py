# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui, QtCore

class Button:
    def create_button(self):
        self.choose_directory_button = QtWidgets.QPushButton('Choose Directory')
        self.choose_directory_button.setStyleSheet('''QPushButton {
                                                          background-color: #394976;
                                                          border-style: hidden;
                                                          border-width: 2px;
                                                          border-radius: 10px;
                                                          border-color: white;
                                                          color: white;
                                                          font: bold 14px;
                                                          font-family: Cera Pro;
                                                          padding: 4px;
                                                      }

                                                      QPushButton:pressed {
                                                          background-color: #303C60;
                                                      }''')
        self.choose_directory_button.setFixedSize(160, 40)
        return self.choose_directory_button


class Label(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, picture, num, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        #print(f'picture->{picture} - {num}')
        self.num = num

        self.setMaximumSize(140, 140)
        self.setMinimumSize(140, 140)
        self.radius = 10 

        self.target = QtGui.QPixmap(self.size())  
        self.target.fill(QtCore.Qt.transparent)    

        p = QtGui.QPixmap(picture).scaled(140, 140, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)

        painter = QtGui.QPainter(self.target)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        path = QtGui.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p)
        self.setPixmap(self.target)

    def mouseReleaseEvent(self, event):
        self.clicked.emit(self.num)