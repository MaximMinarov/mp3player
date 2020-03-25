# -*- coding: utf-8 -*-
import sqlite3, datetime, mutagen, random
from mutagen.id3 import ID3
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui, QtMultimedia
import Design

con = sqlite3.connect('tagsdatabase.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS tags_db(File_Path TEXT,
                                                  Song_Title TEXT,
                                                  Album_Title TEXT,
                                                  Song_Artist TEXT,
                                                  Album_Artist TEXT,
                                                  Year_of_Publishing INTEGER,
                                                  Track_Number INTEGER,
                                                  Length REAL,
                                                  Bitrate INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS covers_db(File_Path TEXT,
                                                    Cover_Path TEXT,
                                                    Album_Title TEXT,
                                                    Album_Artist TEXT,
                                                    Year_of_Publishing INTEGER)''')
con.commit()
con.close()

folder_path = Path(__file__).parent

def extract_cover(path: str, album_title: str, album_artist: str, year_of_publishing:str, con, cur) -> None:
    '''Извлекает обложку из файла'''
  
    random_list = ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g']
    music = ID3(path)
    data = music.getall('APIC')[0].data
    cover_path = False

    if data:
        record = cur.execute('SELECT Cover_Path FROM covers_db WHERE Album_Title=? AND Album_Artist=? AND Year_of_Publishing=?', (album_title, album_artist, year_of_publishing))
        duplicate = record.fetchall()
        cover_name = random.choice(random_list) + random.choice(random_list) + str(random.randint(1000000, 1000000000)) + random.choice(random_list) + random.choice(random_list) + str(random.randint(100, 1000))
        cover_path = str(folder_path) + '\\Covers\\' + cover_name + '.png'
        if duplicate:
            duplicate = (duplicate[0])[0]
            Path.unlink(Path(duplicate))
            cur.execute('UPDATE covers_db SET Cover_Path=?, Album_Title=?, Album_Artist=?, Year_of_Publishing=? WHERE Cover_Path=?', (cover_path, album_title, album_artist, year_of_publishing, duplicate))
            con.commit()
        else:
            cur.execute('INSERT INTO covers_db VALUES(?, ?, ?, ?, ?)', (path, cover_path, album_title, album_artist, year_of_publishing))
        with open(cover_path, 'wb') as cover:
            cover.write(data)

def extract_tags(path: str, con, cur) -> None:
    '''Извлекает теги из файла и заполняет ими базу данных'''

    audiofile = mutagen.File(path)

    if audiofile.tags:

        song_title_f = audiofile.tags.getall('TIT2')
        song_title = str(song_title_f[0]) if song_title_f else 'no song title'
        # Извлекает из MP3-файла название композиции

        album_title_f = audiofile.tags.getall('TALB')
        album_title = str(album_title_f[0]) if album_title_f else 'no album title'
        # Извлекает из MP3-файла название альбома

        song_artist_f = audiofile.tags.getall('TPE1')
        song_artist = str(song_artist_f[0]) if song_artist_f else 'no song artist'
        # Извлекает из MP3-файла имя исполнителя композиции

        album_artist_f = audiofile.tags.getall('TPE2')
        album_artist = str(album_artist_f[0]) if album_artist_f else 'no album artist'
        # Извлекает из MP3-файла имя исполнителя альбома

        year_of_publishing_f = audiofile.tags.getall('TDRC')
        year_of_publishing = str(year_of_publishing_f[0]) if year_of_publishing_f else 'no year of publishing'
        # Извлекает из MP3-файла имя исполнителя альбома

        track_number_f = audiofile.tags.getall('TRCK')
        track_number = str(track_number_f[0]) if track_number_f else 'no track number'
        # Извлекает из MP3-файла порядковый номер композиции

        length = str(datetime.timedelta(seconds = audiofile.info.length))
        # Извлекает из MP3-файла длину композиции

        bitrate = audiofile.info.bitrate
        # Извлекает из MP3-файла битрейт композиции

    song_tags = (path, song_title, album_title, song_artist, album_artist, year_of_publishing, track_number, length, bitrate)

    record = cur.execute('SELECT * FROM tags_db WHERE File_Path=?', (path, ))
    duplicate = record.fetchall()

    if not duplicate:
        cur.execute('INSERT INTO tags_db VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', song_tags)
    else:
        cur.execute('UPDATE tags_db SET Song_Title=?, Album_Title=?, Song_Artist=?, Album_Artist=?, Year_of_Publishing=?, Track_Number=?, Length=?, Bitrate=?  WHERE File_Path=?', (song_title, album_title, song_artist, album_artist, year_of_publishing, track_number, length, bitrate, path))

    con.commit()

    extract_cover(path, album_title, album_artist, year_of_publishing, con, cur)

def choose_files(directory: str, con, cur) -> None:
    pathlist = Path(directory).glob('**/*.mp3')
    if pathlist:
        for path in pathlist:
            path = str(path)
            path = path.replace('\\', '/')
            extract_tags(path, con, cur)
    con.close()

class MyThread(QtCore.QThread):
    def __init__(self, directory, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.directory = directory
    def run(self):
        print('THREAD: run')
        con = sqlite3.connect('tagsdatabase.db')
        cur = con.cursor()
        choose_files(self.directory, con, cur)

class MyWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet('background: #222E49;')

        self.dict = {}
        self.song = ''
        self.play_repeat = True
        self.play_pause = True
        self.current_index = 1

        self.ButtonCopy = Design.Button()
        self.listWidget = Design.ListWidget()

        self.box1 = QtWidgets.QGridLayout(self)
        self.box2 = QtWidgets.QVBoxLayout()

        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet('background: white;')
        self.container.setMinimumSize(250, 300)
        self.container.setMaximumWidth(350)
        self.box2.addWidget(self.container)
        self.box5 = QtWidgets.QVBoxLayout(self.container)

        self.container2 = QtWidgets.QWidget()
        self.container2.setStyleSheet('background: white;')
        self.container2.setMinimumSize(250, 300)
        self.container2.setMaximumWidth(350)
        self.box2.addWidget(self.container2)
        self.box6 = QtWidgets.QVBoxLayout(self.container2)
        self.container2.hide()

        container = QtWidgets.QWidget()
        container.setStyleSheet('background: yellow;')
        container.setMinimumWidth(250)
        container.setMaximumSize(350, 40)
        self.box2.addWidget(container)
        self.box4 = QtWidgets.QHBoxLayout(container)

        self.btn1 = QtWidgets.QPushButton('Page1')
        self.btn1.clicked.connect(lambda: self.make_page(1))
        self.box4.addWidget(self.btn1)
        self.btn2 = QtWidgets.QPushButton('Page2')
        self.btn2.clicked.connect(lambda: self.make_page(2))
        self.box4.addWidget(self.btn2)

        self.art = Design.Label('album.png', 150)
        self.box5.addStretch(3)
        self.box5.addWidget(self.art, alignment=QtCore.Qt.AlignCenter)

        self.song_title = QtWidgets.QLabel('Song Title')
        self.box5.addStretch(2)
        self.box5.addWidget(self.song_title, alignment=QtCore.Qt.AlignCenter)

        self.artist = QtWidgets.QLabel('Artist')
        self.box5.addStretch(1)
        self.box5.addWidget(self.artist, alignment=QtCore.Qt.AlignCenter)

        self.const_btn = QtWidgets.QPushButton('Play', clicked = self.const_play)
        self.box5.addStretch(2)
        self.box5.addWidget(self.const_btn, alignment=QtCore.Qt.AlignCenter)

        self.player = QtMultimedia.QMediaPlayer()
        self.player.stateChanged.connect(self.player_state)

        self.qsl = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.qsl.sliderMoved[int].connect(self.set_play_position)
        self.qsl.sliderReleased.connect(self.slider_released)
        self.qsl.setEnabled(False)
        self.box5.addStretch(1)
        self.box5.addWidget(self.qsl)

        self.repeat_btn = QtWidgets.QPushButton('Repeat', clicked = self.repeat)
        self.box5.addStretch(2)
        self.box5.addWidget(self.repeat_btn, alignment=QtCore.Qt.AlignCenter)
        self.box5.addStretch(3)

        self.choose_dir_btn = self.ButtonCopy.create_button()
        self.choose_dir_btn.clicked.connect(self.choose_dir_thread)
        self.box6.addWidget(self.choose_dir_btn)

        self.back_btn = QtWidgets.QPushButton('Back', clicked = self.back)
        self.box2.addWidget(self.back_btn, alignment=QtCore.Qt.AlignCenter)
        self.back_btn.hide() 

        self.box1.addWidget(self.listWidget, 0, 0)
        self.box1.addLayout(self.box2, 0, 1)
        self.box1.setColumnStretch(1, 1)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.play_mode)
        self.timer.start(1000)


        self.create_albums_list()

    def choose_dir_thread(self):
        print('CHOOSE DIRECTORY BUTTON: click')
        self.directory = self.choose_dir()
        if self.directory:
            self.mythread = MyThread(self.directory)
            self.mythread.started.connect(self.on_started)
            self.mythread.finished.connect(self.on_finished)
            self.mythread.start()

    def choose_dir(self):
        print('dialog window')
        drive = Path().absolute().drive + '/'
        dir_1 = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                           'Open a folder',
                                                           drive,
                                                           QtWidgets.QFileDialog.ShowDirsOnly)
        if dir_1:
            return dir_1

    def on_started(self):
        print('THREAD: start')

    def on_finished(self):
        print('THREAD: finish')

    def create_albums_list(self):
        self.con = sqlite3.connect('tagsdatabase.db')
        self.cur = self.con.cursor()

        albums_list = self.cur.execute('SELECT Cover_Path FROM covers_db')
        albums_list = albums_list.fetchall()

        self.create_albums(albums_list)

    def create_albums(self, albums_list):
        for album in albums_list:
            art = Design.Label(album[0], 150)
            art.clicked.connect(lambda album=album[0]: self.click(album))
            self.listWidget.makeItem(art)

    def click(self, album):
        self.album = album
        self.scrollArea = QtWidgets.QScrollArea()
        container = QtWidgets.QWidget()
        self.scrollArea.setWidget(container)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.box3 = QtWidgets.QGridLayout(container)
        self.box1.addWidget(self.scrollArea, 0, 0)
        self.create_list()
        self.back_btn.show()

    def create_list(self):
        self.song_list = []
        album_info = self.cur.execute('SELECT Album_Title, Album_Artist, Year_of_Publishing FROM covers_db WHERE Cover_Path=?', (self.album,))
        album_info = (album_info.fetchall())[0]
        tracks_info = self.cur.execute('SELECT File_Path, Song_Title FROM tags_db WHERE Album_Title = ? AND Album_Artist = ? AND Year_of_Publishing = ?', (album_info[0], album_info[1], album_info[2]))
        tracks_info = tracks_info.fetchall()
        row = 0
        for song in tracks_info:
            self.dict[song[0]] = []
            song_label = QtWidgets.QLabel(song[1])
            play_btn = QtWidgets.QPushButton('Play', clicked = lambda ch, song = song[0]: self.play(song))
            if (song[0] == self.song) and (self.play_pause == False):
                play_btn.setText("Pause")
            self.dict[song[0]].append(play_btn)
            self.dict[song[0]].append(song[1])
            self.dict[song[0]].append(self.album)
            self.box3.addWidget(song_label, row, 0)
            self.box3.addWidget(play_btn, row, 1)           
            row = row + 1
        #print(self.dict)

    def back(self):
        self.back_btn.hide()
        self.listWidget = Design.ListWidget()
        self.dict = {}
        self.create_albums_list()
        self.box1.addWidget(self.listWidget, 0, 0)

    def play_mode(self):
        if self.play_pause == False:
            self.qsl.setMinimum(0)
            self.qsl.setMaximum(self.player.duration())
            self.qsl.setValue(self.qsl.value() + 1000)

    def slider_released(self):
        self.player.setPosition(self.qsl.value())

    def set_play_position(self, val):
        pass

    def play(self, song):
        if self.song != song:
            if self.player.isAudioAvailable() == True:
                if self.song in self.dict:
                    self.dict[self.song][0].setText("Play")
            self.player.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl(song)))
            self.song = song
            self.player.play()
            self.play_pause = False
            self.qsl.setEnabled(True)
            self.dict[song][0].setText("Pause")
            self.song_title.setText(self.dict[self.song][1])
            self.art.setPicture(self.dict[self.song][2])
            self.const_btn.setText("Pause")
        else:
            if self.play_pause == True:
                self.player.play()
                self.play_pause = False
                self.qsl.setEnabled(True)
                self.dict[song][0].setText("Pause")
                self.const_btn.setText("Pause")
            else:
                self.player.pause()
                self.play_pause = True
                self.dict[song][0].setText("Play")

    def const_play(self):
        if self.player.isAudioAvailable() == True:
            if self.play_pause == True:
                self.player.play()
                self.play_pause = False
                self.qsl.setEnabled(True)
                self.const_btn.setText("Pause")
                if self.song in self.dict:
                    self.dict[self.song][0].setText("Pause")
            else:
                self.player.pause()
                self.play_pause = True
                self.const_btn.setText("Play")
                if self.song in self.dict:
                    self.dict[self.song][0].setText("Play")

    def player_state(self, state):
        if state == 0:
            if self.play_repeat == True:
                self.qsl.setSliderPosition(0)
                self.player.play()
            else:
                self.play_pause = True
                self.qsl.setSliderPosition(0)
                self.qsl.setEnabled(False)
                self.const_btn.setText("Play")
                if self.song in self.dict:
                    self.dict[self.song][0].setText("Play")

    def repeat(self):
        if self.play_repeat == False:
            self.play_repeat = True
            self.repeat_btn.setText("Repeat")   
        else:
            self.play_repeat = False
            self.repeat_btn.setText("Not Repeat")

    def make_page(self, index):
        if (self.current_index != 1) and (index == 1):
            self.current_index = 1

            self.container2.hide()
            self.container.show()
        
        if (self.current_index != 2) and (index == 2):
            self.current_index = 2

            self.container.hide()
            self.container2.show()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle(' ')
    window.show()
    sys.exit(app.exec_())
