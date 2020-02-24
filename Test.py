from PyQt5 import QtCore, QtWidgets, QtMultimedia

class MyWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = ['1.Papercut.mp3', '13.Numb.mp3']

        self.player = QtMultimedia.QMediaPlayer()

        self.box = QtWidgets.QGridLayout(self)      

        play_btn = QtWidgets.QPushButton('Play', clicked = self.play_song)
        self.box.addWidget(play_btn, 0, 0)

    # Воспроизведение
    def play_song(self, song):
        self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl(self.list[1])))
        self.player.play()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle('MP3-player, PyQt5')
    window.show()
    sys.exit(app.exec_())
