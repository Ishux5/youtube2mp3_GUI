from threading import Thread
from pathlib import Path
import PySimpleGUI as sg
import json
from error_GUI import errorWindow
from download_mp3 import youtube2mp3
from os import listdir
from os.path import isfile, join


def getDataList(data):
    dList = [[], []]
    for title in list(data):
        dList[0].append(data[title]["newartist"])
        dList[1].append(data[title]["newtitle"])
    return dList


def download_GUI(data, songSavePath):
    sg.set_options(font=('Courier New', 11))
    sizes = [30, 40, 20]
    dataList = getDataList(data)
    downloading = None
    started = []
    finished = []

    progress = []
    for song in data:
        progress.append(
            [sg.ProgressBar(max_value=100, orientation="h", key=f"progress {song}", size=(sizes[2], 12))])

    listbox = [
        [
            sg.Text("Artist".center(sizes[0]), pad=(0, 0)),
            sg.Text("Title".center(sizes[1]), pad=(0, 0)),
            sg.Text("Progress".center(25), pad=(0, 0))
        ],
        [
            sg.Listbox(dataList[0], size=(
                sizes[0], len(list(data))), no_scrollbar=True, key="listbox 1", pad=(0, 0)),
            sg.Listbox(dataList[1], size=(
                sizes[1], len(list(data))), no_scrollbar=True, key="listbox 2", pad=(0, 0)),
            sg.Column(progress)
        ]
    ]

    layout = [
        [
            sg.Column(listbox, scrollable=True,
                      vertical_scroll_only=True, size=(900, 600))
        ],
        [
            sg.Text("single Download:", pad=(0, 0)),
            sg.Button("OFF", button_color="white on red",
                      key="-TOGGLE SDL-", size=(4, 1)),
            sg.Button("Start", size=(33, 1), key="start dl"),
            sg.Button("Pause", size=(20, 1), key="pause dl"),
            sg.Button("Resume", size=(20, 1), key="resume dl")
        ]
    ]

    window = sg.Window("download", layout, finalize=True)
    SDL = False
    # create list of all songnames files
    songFiles = []
    for song in data:
        songFiles.append(data[song]["newartist"] +
                         " - " + data[song]["newtitle"] + ".mp3")

    while True:
        event, value = window.read(timeout=100)
        #window["progress 0"].UpdateBar(50)
        if event == sg.WIN_CLOSED:
            break

        if event == "-TOGGLE SDL-":
            SDL = not SDL
            window["-TOGGLE SDL-"].update(text="ON" if SDL else "OFF",
                                          button_color="white on green" if SDL else "white on red")

        if event == "start dl":
            downloading = True
            Path(songSavePath + "\songs").mkdir(exist_ok=True)
            for song in data:
                if downloading and not SDL:
                    started.append(song)
                    Thread(target=youtube2mp3, args=(
                        data[song]["videoID"], data[song]["newartist"], data[song]["newtitle"], songSavePath + "\songs")).start()

        if event == "pause dl":
            print("paused")
            downloading = False

        if event == "resume dl":
            if downloading == None:
                errorWindow("Download has not been started!")
            else:
                downloading = True

        # see if song is finished downloading
        length = len(finished)
        try:
            finished = [f for f in listdir(
                songSavePath + "\\songs") if isfile(join(songSavePath + "\\songs", f))]
        except:
            pass
        # update progressbar if started
        for file in started:
            window[f"progress {file}"].UpdateBar(50)

        # update progressbar if finished
        for file in finished:
            artist, title = file[:-
                                 4].rsplit(" - ")[0], file[:-4].rsplit(" - ")[1]
            for song in data:
                if data[song]["newartist"] == artist and data[song]["newtitle"] == title:
                    videoID = data[song]["videoID"]
                    window[f"progress {videoID}"].UpdateBar(100)

    window.close()


if __name__ == '__main__':
    Adata = json.load(open("items/Normal1/changed.json"))
    download_GUI(
        Adata, "E:\\Krims-Krams-Ecke D\\OneDrive\\Projekte\\Programieren\\Python\\Playlist Downloader\\items\\Normal1")
