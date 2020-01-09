import mutagen
import datetime

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
# import pygame

import sqlite3
from mutagen.id3 import ID3
from tkinter import *
from tkinter.filedialog import askdirectory

con = sqlite3.connect('tagsdatabase.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS tags_db(Song_Path TEXT,
                                                  Song_Title TEXT,
                                                  Album_Title TEXT,
                                                  Song_Artist TEXT,
                                                  Album_Artist TEXT,
                                                  Year_of_Publishing INTEGER,
                                                  Track_Number INTEGER,
                                                  Length REAL,
                                                  Bitrate INTEGER)''')

cur.execute('''CREATE TABLE IF NOT EXISTS covers_db(Cover_Path TEXT,
                                                    Song_Title TEXT,
                                                    Album_Title TEXT,
                                                    Album_Artist TEXT,
                                                    Year_of_Publishing INTEGER)''')
con.commit()

ban = str.maketrans('', '', '\:')
folder_path = os.path.dirname(__file__)

root = Tk()
root.minsize(300, 300)


def extract_cover(path: str) -> None:
    '''Извлекает обложку из файла.'''
    music = ID3(path)
    data = music.getall('APIC')[0].data
    cover_name_f = path.translate(ban)
    cover_name_s = cover_name_f.replace('.mp3', '')

    with open(folder_path + '/Covers/' + cover_name_s + '.png', 'wb') as cover:
        cover.write(data)


def extract_tags(path: str) -> str:
    '''Извлекает теги из файла и заполняет ими базу данных.'''

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

    record_f = cur.execute('SELECT * FROM tags_db WHERE Song_Path=?', (path, ))
    record = record_f.fetchall()

    if not record:
        cur.execute('INSERT INTO tags_db VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', song_tags)
    else:
        cur.execute('UPDATE tags_db SET Song_Title=?, Album_Title=?, Song_Artist=?, Album_Artist=?, Year_of_Publishing=?, Track_Number=?, Length=?, Bitrate=?  WHERE Song_Path=?', (song_title, album_title, song_artist, album_artist, year_of_publishing, track_number, length, bitrate, path))

    con.commit()

    extract_cover(path)


def choose_files(directory: str) -> None:
    '''Отбирает MP3-файлы из ввыбранной директории, применяет extract_tags к каждому из них.'''
    for file in os.listdir(directory):
        if file.endswith('.mp3'):
            path = os.path.realpath(file)
            extract_tags(path)


def choose_directory(event) -> None:
    '''Открывает диалоговое окно выбора директории с MP3-файлами'''
    directory = askdirectory()
    os.chdir(directory)
    choose_files(directory)

    # exit()


choosedirectory = Button(root, text = 'Choose Directory')
choosedirectory.pack()
choosedirectory.bind('<Button-1>', choose_directory)

root.mainloop()
