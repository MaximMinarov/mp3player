import mutagen
import datetime

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# import pygame


import sqlite3
from mutagen.id3 import ID3
from tkinter import *
from tkinter.filedialog import askdirectory
 
con = sqlite3.connect("tagsdatabase.db")
cursor = con.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS tags_db(Path TEXT,
                                                     Song_Title TEXT,
                                                     Album_Title TEXT,
                                                     Song_Artist TEXT,
                                                     Album_Artist TEXT,
                                                     Year_of_Publishing INTEGER,
                                                     Track_Number INTEGER,
                                                     Length REAL,
                                                     Bitrate INTEGER)''')
con.commit()

root = Tk()
root.minsize(300, 300)


def extract_tags(path: str) -> None:
    '''Функция получает путь до MP3-файла, извлекает из него теги и заполняет ими базу данных.'''

    audiofile = mutagen.File(path)

    if audiofile.tags:

        song_title = audiofile.tags.getall('TIT2')
        SongTitle = str(song_title[0]) if song_title else None
        '''Метод извлекает из MP3-файла название композиции.'''

        album_title = audiofile.tags.getall('TALB')
        AlbumTitle = str(album_title[0]) if album_title else None
        '''Метод извлекает из MP3-файла название альбома.'''

        song_artist = audiofile.tags.getall('TPE1')
        SongArtist = str(song_artist[0]) if song_artist else None
        '''Метод извлекает из MP3-файла имя исполнителя композиции.'''

        album_artist = audiofile.tags.getall('TPE2')
        AlbumArtist = str(album_artist[0]) if album_artist else None
        '''Метод извлекает из MP3-файла имя исполнителя альбома.'''

        year_of_publishing = audiofile.tags.getall('TDRC')
        YearOfPublishing = str(year_of_publishing[0]) if year_of_publishing else None
        '''Метод извлекает из MP3-файла имя исполнителя альбома.'''

        track_number = audiofile.tags.getall('TRCK')
        TrackNumber = str(track_number[0]) if track_number else None
        '''Метод извлекает из MP3-файла порядковый номер композиции.'''

        Length = str(datetime.timedelta(seconds=audiofile.info.length))
        '''Метод извлекает из MP3-файла длину композиции.'''

        Bitrate = audiofile.info.bitrate
        '''Метод извлекает из MP3-файла битрейт композиции.'''

    SongTags = (path, SongTitle, AlbumTitle, SongArtist, AlbumArtist, YearOfPublishing, TrackNumber, Length, Bitrate)
    cursor.execute('INSERT INTO tags_db VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', SongTags)
    con.commit()


def choose_files(directory: str) -> None:
    '''Функция получает путь к директории, отбирает MP3-файлы, применяет extract_tags к каждому из них.'''
    for file in os.listdir(directory):
        if file.endswith(".mp3"):
            path = os.path.realpath(file)
            extract_tags(path)


def choose_directory(event) -> None:
    '''Функция открывает диалоговое окно выбора директории с MP3-файлами'''
    directory = askdirectory()
    os.chdir(directory)
    choose_files(directory)

    # exit()


choosedirectory = Button(root, text = 'Choose Directory')
choosedirectory.pack()
choosedirectory.bind("<Button-1>", choose_directory)

root.mainloop()
