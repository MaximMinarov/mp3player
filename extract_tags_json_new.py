import mutagen
import datetime

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# import pygame

import json
from mutagen.id3 import ID3
from tkinter import *
from tkinter.filedialog import askdirectory

root = Tk()
root.minsize(300, 300)
all_tags = {}


def write_tags() -> None:
    '''Функция записывает словарь 'all_tags' в JSON-файл.'''
    with open("C:\\Users\\101ap\\Desktop\\Player\\tags.json", 'w') as t:
        json.dump(all_tags, t, indent = 4, ensure_ascii = False)


def extract_tags(path) -> None:
    '''Функция получает путь до MP3-файла, извлекает из него теги и наполняет ими
       словарь 'song_tags', который передает в словарь 'all_tags'.'''

    audiofile = mutagen.File(path)

    # print(path, audiofile)

    song_tags = {}
    song_tags['Path to the File'] = path

    if audiofile.tags:

        song_title = audiofile.tags.getall('TIT2')
        song_tags['Song Title'] = str(song_title[0]) if song_title else None
        '''Метод извлекает из MP3-файла название композиции.'''

        album_title = audiofile.tags.getall('TALB')
        song_tags['Album Title'] = str(album_title[0]) if album_title else None
        '''Метод извлекает из MP3-файла название альбома.'''

        song_artist = audiofile.tags.getall('TPE1')
        song_tags['Song Artist'] = str(song_artist[0]) if song_artist else None
        '''Метод извлекает из MP3-файла имя исполнителя композиции.'''

        album_artist = audiofile.tags.getall('TPE2')
        song_tags['Album Artist'] = str(album_artist[0]) if album_artist else None
        '''Метод извлекает из MP3-файла имя исполнителя альбома.'''

        year_of_publishing = audiofile.tags.getall('TDRC')
        song_tags['Year of Publishing'] = str(year_of_publishing[0]) if year_of_publishing else None
        '''Метод извлекает из MP3-файла имя исполнителя альбома.'''

        track_number = audiofile.tags.getall('TRCK')
        song_tags['Track Number'] = str(track_number[0]) if track_number else None
        '''Метод извлекает из MP3-файла порядковый номер композиции.'''

        song_tags['Length'] = str(datetime.timedelta(seconds=audiofile.info.length))
        '''Метод извлекает из MP3-файла длину композиции.'''

        song_tags['Bitrate'] = audiofile.info.bitrate
        '''Метод извлекает из MP3-файла битрейт композиции.'''

    return song_tags


def choose_files(directory: str) -> None:
    '''Функция получает путь к директории, отбирает MP3-файлы,
       применяет extract_tags к каждому из них.'''
    for file in os.listdir(directory):
        if file.endswith(".mp3"):
            path = os.path.realpath(file)
            all_tags[path] = extract_tags(path)
    write_tags()


def choose_directory(event) -> None:
    '''Функция открывает диалоговое окно выбора директории с MP3-файлами'''
    directory = askdirectory()
    os.chdir(directory)
    choose_files(directory)

    exit()


choosedirectory = Button(root, text = 'Choose Directory')
choosedirectory.pack()
choosedirectory.bind("<Button-1>", choose_directory)

root.mainloop()
