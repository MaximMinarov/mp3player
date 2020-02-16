# -*- coding: utf-8 -*-
import sqlite3, datetime, mutagen, random
from mutagen.id3 import ID3
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui
from PIL import Image, ImageDraw
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

random_list = ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g']
folder_path = Path(__file__).parent

def extract_cover(path: str, album_title: str, album_artist: str, year_of_publishing:str, con, cur) -> None:
    '''Извлекает обложку из файла'''

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
        self.setStyleSheet('background: #27304F;')
        self.setMinimumSize(600, 400)
        self.ButtonCopy = Design.Button()
        self.box1 = QtWidgets.QGridLayout()
        self.box2 = QtWidgets.QVBoxLayout()
        self.button = self.ButtonCopy.create_button()
        self.box2.addWidget(self.button, alignment=QtCore.Qt.AlignRight) 
        self.box1.addLayout(self.box2, 0, 1)
        self.button.clicked.connect(self.choose_dir_thread)
        self.setLayout(self.box1)
        self.create_albums()

    def choose_dir_thread(self):
        print('CHOOSE DIRECTORY BUTTON: click')
        self.directory = self.choose_dir()
        if self.directory:
            # THREAD #
            self.mythread = MyThread(self.directory)
            self.mythread.started.connect(self.on_started)
            self.mythread.finished.connect(self.on_finished)
            self.mythread.start()
            # ------ #

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

    def create_albums(self):
        con = sqlite3.connect('tagsdatabase.db')
        cur = con.cursor()
        self.albums_list = []
        albums_f = cur.execute('SELECT Cover_Path FROM covers_db')
        albums_s = albums_f.fetchall()

        for album in albums_s:
            self.albums_list.append(album[0])

        self.box3 = QtWidgets.QGridLayout()
        self.box3.setSpacing(20)

        line = 0
        column = 0

        for album_ in self.albums_list:
            label = Design.Label(album_, album_)
            label.clicked.connect(lambda num=album_: self.click(num, con, cur))
            self.box3.addWidget(label, line, column)
            column = column + 1
        self.box1.addLayout(self.box3, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        self.box1.setColumnStretch(0, 1) 

    def click(self, album, con, cur):
        self.delete()
        self.create_list(album, con, cur)
        self.back_button = QtWidgets.QPushButton('Back')
        self.back_button.clicked.connect(self.back_button_func)
        self.box2.addWidget(self.back_button)

    def create_list(self, album, con, cur):
        self.song_list = []
        album_info_1 = cur.execute('SELECT Album_Title, Album_Artist, Year_of_Publishing FROM covers_db WHERE Cover_Path=?', (album,))
        album_info = (album_info_1.fetchall())[0]
        tracks_info_1 = cur.execute('SELECT File_Path, Song_Title FROM tags_db WHERE Album_Title = ? AND Album_Artist = ? AND Year_of_Publishing = ?', (album_info[0], album_info[1], album_info[2]))
        tracks_info = tracks_info_1.fetchall()
        row = 0
        for song in tracks_info:
            self.song_button = QtWidgets.QPushButton(song[1])
            self.box3.addWidget(self.song_button, row, 0)
            row = row + 1
    
    def delete(self):
        for row in range(self.box3.rowCount()):
            for col in range(self.box3.columnCount()):
                w = self.box3.itemAtPosition(row, col).widget()
                w.deleteLater()

    def delete2(self):
        col = 0
        self.back_button.deleteLater()
        for row in range(self.box3.rowCount()):
            w = self.box3.itemAtPosition(row, col).widget()
            w.deleteLater()

    def back_button_func(self):
        self.delete2()
        self.create_albums()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle(' ')
    window.show()
    sys.exit(app.exec_())
