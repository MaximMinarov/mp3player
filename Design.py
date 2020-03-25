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
        #self.choose_directory_button.setFixedSize(250, 40)
        return self.choose_directory_button


class Label(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, picture, x, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)

        self.x = x

        self.setMaximumSize(self.x, self.x)
        self.setMinimumSize(self.x, self.x)
        self.radius = 10 

        self.setPicture(picture)

    def setPicture(self, picture):
        target = QtGui.QPixmap(self.size())
        target.fill(QtCore.Qt.transparent)

        p = QtGui.QPixmap(picture).scaled(
            self.x, self.x, QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )

        painter = QtGui.QPainter(target)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        path = QtGui.QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p)
        self.setPixmap(target)

        painter.end()
        target = None

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class ListWidget(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
        self.setStyleSheet('border-style: hidden;')
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(self.NoEditTriggers)
        self.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.setSelectionMode(self.ContiguousSelection)
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        self.setSpacing(14)
        #self._rubberPos  = None
        #self._rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def makeItem(self, lb):
        item = QtWidgets.QListWidgetItem(self)
        item.setSizeHint(QtCore.QSize(140, 140))
        self.setItemWidget(item, lb)
