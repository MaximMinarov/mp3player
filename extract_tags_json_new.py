import mutagen, datetime, pygame, os, json
from mutagen.id3 import ID3
from tkinter import *
from tkinter.filedialog import askdirectory

root = Tk()
root.minsize(300,300)
all_tags={}

def write_tags() -> None:
    '''Функция записывает словарь 'all_tags' в JSON-файл.'''
    with open("C:\\Users\\101ap\\Desktop\\Player\\tags.json", 'w') as t:       
        json.dump(all_tags, t, indent=4)


def extract_tags(audiofile: str) -> None:
    '''Функция получает путь к MP3-файлу, извлекает из него теги, наполняет ими
       словарь 'song_tags', который передает в словарь 'all_tags' и вызывает
       функцию 'write_tags'.'''
    song_tags = {}
    song_tags['Path to the File']=audiofile
    song_title = audiofile.tags.getall('TIT2')
    song_tags['Song Title'] = str(song_title[0])
    '''Метод извлекает из MP3-файла название композиции.'''
    album_title = audiofile.tags.getall('TALB')
    song_tags['Album Title'] = str(album_title[0])
    '''Метод извлекает из MP3-файла название альбома.'''
    song_artist = audiofile.tags.getall('TPE1')
    song_tags['Song Artist'] = str(song_artist[0])
    '''Метод извлекает из MP3-файла имя исполнителя композиции.'''
    album_artist = audiofile.tags.getall('TPE2')
    song_tags['Album Artist'] = str(album_artist[0])
    '''Метод извлекает из MP3-файла имя исполнителя альбома.'''
    year_of_publishing = audiofile.tags.getall('TDRC')
    song_tags['Year of Publishing'] = str(year_of_publishing[0])
    '''Метод извлекает из MP3-файла имя исполнителя альбома.'''
    track_number = audiofile.tags.getall('TRCK')
    song_tags['Track Number'] = str(track_number[0])
    '''Метод извлекает из MP3-файла порядковый номер композиции.'''
    song_tags['Length'] = str(datetime.timedelta(seconds=audiofile.info.length))
    '''Метод извлекает из MP3-файла длину композиции.'''
    song_tags['Bitrate'] = audiofile.info.bitrate
    '''Метод извлекает из MP3-файла битрейт композиции.'''
    all_tags[audiofile]=song_tags
    write_tags()


def choose_files(directory: str) -> None:
    '''Функция получает путь к директории, отбирает MP3-файлы и вызывает
       функцию 'extract_tags'.'''
    for files in os.listdir(directory):
        if files.endswith(".mp3"):
            realdir = os.path.realpath(files)
            audiofile = mutagen.File(realdir)
            return audiofile
            extract_tags(audiofile)


def choose_directory(event) -> str:
    '''Функция открывает диалоговое окно выбора директории с MP3-файлами,
       возвращает путь к ней и вызывает функию 'choose_files'.'''
    directory = askdirectory()
    os.chdir(directory)
    return directory
    choose_files(directory)


choosedirectory=Button(root,text='Choose Directory')
choosedirectory.pack()
choosedirectory.bind("<Button-1>", choose_directory)

root.mainloop()
