import mutagen
import datetime

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

import sqlite3
from mutagen.id3 import ID3
from tkinter import *
from tkinter.filedialog import askdirectory
from PIL import ImageTk
from PIL import Image

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

ban = str.maketrans('', '', '\:')
folder_path = os.path.dirname(__file__)

root = Tk()
root.minsize(800, 600)
root.maxsize(800, 600)


def create_frame():
    '''Создает новый фрейм'''
    frame = Frame(root, height = 400, width = 800, bg = 'gray')
    frame.place(x = 0, y = 60)
    return frame

frame = create_frame()


def resize(filename: str) -> None:
    '''Изменяет размер обложки'''
    img = Image.open(filename)
    img.thumbnail((120, 120), Image.ANTIALIAS)
    img.save(filename)


def extract_cover(path: str, album_title: str, album_artist: str, year_of_publishing:str) -> None:
    '''Извлекает обложку из файла'''

    music = ID3(path)
    data = music.getall('APIC')[0].data
    cover_path = False

    if data:

        record_one = cur.execute('SELECT * FROM covers_db WHERE Album_Title=? AND Album_Artist=? AND Year_of_Publishing=?', (album_title, album_artist, year_of_publishing))
        duplicate_one = record_one.fetchall()

        record_two = cur.execute('SELECT * FROM covers_db WHERE File_Path=?', (path, ))
        duplicate_two = record_two.fetchall()

        if not duplicate_one:
            cover_name_f = path.translate(ban)
            cover_name_s = cover_name_f.replace('.mp3', '')
            cover_path = folder_path + '/Covers/' + cover_name_s + '.png'
            cur.execute('INSERT INTO covers_db VALUES(?, ?, ?, ?, ?)', (path, cover_path, album_title, album_artist, year_of_publishing))
            with open(cover_path, 'wb') as cover:
                cover.write(data)

        if duplicate_two:
            cur.execute('UPDATE covers_db SET Cover_Path=?, Album_Title=?, Album_Artist=?, Year_of_Publishing=? WHERE File_Path=?', (cover_path, album_title, album_artist, year_of_publishing, path))

        con.commit()

    if cover_path:
        resize(cover_path)


def extract_tags(path: str) -> None:
    '''Извлекает теги из файла и заполняет ими базу данных'''

    audiofile = mutagen.File(path)

    if audiofile.tags:

        song_title_f = audiofile.tags.getall('TIT2')
        song_title = str(song_title_f[0]) if song_title_f else None
        # Извлекает из MP3-файла название композиции

        album_title_f = audiofile.tags.getall('TALB')
        album_title = str(album_title_f[0]) if album_title_f else None
        # Извлекает из MP3-файла название альбома

        song_artist_f = audiofile.tags.getall('TPE1')
        song_artist = str(song_artist_f[0]) if song_artist_f else None
        # Извлекает из MP3-файла имя исполнителя композиции

        album_artist_f = audiofile.tags.getall('TPE2')
        album_artist = str(album_artist_f[0]) if album_artist_f else None
        # Извлекает из MP3-файла имя исполнителя альбома

        year_of_publishing_f = audiofile.tags.getall('TDRC')
        year_of_publishing = str(year_of_publishing_f[0]) if year_of_publishing_f else None
        # Извлекает из MP3-файла имя исполнителя альбома

        track_number_f = audiofile.tags.getall('TRCK')
        track_number = str(track_number_f[0]) if track_number_f else None
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

    extract_cover(path, album_title, album_artist, year_of_publishing)


def choose_files(directory: str) -> None:
    '''Отбирает MP3-файлы из выбранной директории и применяет extract_tags к каждому из них'''
    for file in os.listdir(directory):
        if file.endswith('.mp3'):
            path = os.path.realpath(file)
            extract_tags(path)
    create_albums(frame)
    # con.close()


def choose_directory() -> None:
    '''Открывает окно выбора директории с MP3-файлами'''
    directory = askdirectory()
    os.chdir(directory)
    choose_files(directory)


def stop(button):
    '''Останавливает воспроизведение композиции'''
    pygame.mixer.music.stop()
    button.place_forget()


def play(song, y, frame):
    '''Воспроизводит композицию'''
    pygame.mixer.init()
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    stop_button = Button(frame,
                         text = 'Stop',
                         font ='CeraPro-Bold')
    stop_button.config(command = lambda widget = stop_button: stop(widget))
    stop_button.place(x = 200, y = y)


def back(button):
    '''Возращает к списку альбомов'''
    frame = create_frame()
    button.place_forget()
    create_albums(frame)


def create_list(album_title):
    '''Создает список композиций'''
    frame = create_frame()
    album_info_1 = cur.execute('SELECT Album_Title, Album_Artist, Year_of_Publishing FROM covers_db WHERE Cover_Path=?', (album_title,))
    album_info = (album_info_1.fetchall())[0]
    tracks_info_1 = cur.execute('SELECT File_Path, Song_Title FROM tags_db WHERE Album_Title = ? AND Album_Artist = ? AND Year_of_Publishing = ?', (album_info[0], album_info[1], album_info[2]))
    tracks_info = tracks_info_1.fetchall()
    y = 40
    for song in tracks_info:
        song_button = Button(frame,
                             text = song[1],
                             font ='CeraPro-Bold',
                             command = lambda song=song, y=y: play(song[0], y, frame))
        song_button.place(x = 20, y = y)
        y = y + 40
    back_button = Button(root,
                         text = 'Back',
                         font ='CeraPro-Bold')
    back_button.config(command = lambda widget = back_button: back(widget))
    back_button.place(x = 100, y = 10)


def create_albums(frame) -> None:
    '''Создает список альбомов'''
    albums_list = []

    albums_f = cur.execute('SELECT Cover_Path FROM covers_db')
    albums_s = albums_f.fetchall()
    
    if albums_s:

        number = len(albums_s)
        xy = []
        i = 1
        x = 20
        y = 50

        while i <= number:
            xy.append([x, y])
            i = i + 1
            x = x + 140
            if i % 7 == 0:
                x = 30
                y = y + 140

        for album in albums_s:
            albums_list.append(album[0])

        k = 0

        for album_1 in albums_list:
            image = ImageTk.PhotoImage(file = str(album_1))

            album_button = Button(frame,
                                  image = image,
                                  width = 120, height = 120,
                                  command = lambda album_title = album_1: create_list(album_title))
            album_button.image = image
            album_button.place(x = (xy[k])[0], y = (xy[k])[1])
            k = k + 1


create_albums(frame)


choose_directory_button = Button(root,
                                 text = 'Choose Directory',
                                 font ='CeraPro-Bold',
                                 command = lambda: choose_directory())
choose_directory_button.place(x = 300, y = 10)

root.mainloop()
