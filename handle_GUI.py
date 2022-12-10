import googleapiclient.discovery
import PySimpleGUI as sg
from webbrowser import open as wbopen
from pyperclip import copy
import json
import os
from overview_GUI import overview_GUI
from youtube_title_parse import get_artist_title
from error_GUI import errorWindow
from handle_select_GUI import getAPIKEY


def main_GUI():
    with open("items/config.txt") as file:
        folderName = "".join(file.readlines())

    config_json = "items/" + folderName + "/config.json"
    titles_json = "items/" + folderName + "/titles.json"
    changed_json = "items/" + folderName + "/changed.json"
    skipped_json = "items/" + folderName + "/skipped.json"

    apiKey = getAPIKEY("credentials\credentials.json")
    apiName = "youtube"
    apiVersion = "v3"

    forbiddenCharacters = """<>:"'/\|?*"""

    sg.set_options(font=("Courier New", 12))

    # GUI layout
    title_layout = [
        [sg.Text("Titles")],
        [sg.Listbox(values=[], size=(40, 32),
                    enable_events=True, key="-TITLES BOX-")]
    ]

    b1_layout = [
        [sg.Button("->", key="-M TS-")],
        [sg.Button("<-", key="-M ST-")],
        [sg.Button("<<-", key="-MA ST-")]
    ]

    b2_layout = [
        [sg.Button("->", key="-M SC-")],
        [sg.Button("<-", key="-M CS-")]
    ]

    left_input_layout = [
        [sg.Button("add selected to Artist", size=(40, 1), key="-ADD ARTIST-")],
        [sg.Text("Artist:")],
        [sg.Input("", size=(40, 1), key="-ARTIST INP-")],
        [sg.Button("Skip Title", size=(40, 1), key="-TITLE SKIP-")],
        [sg.Text("Skipped Titles:")],
        [sg.Listbox(values=[], size=(40, 20),
                    enable_events=True, key="-SK TITLE BOX-", horizontal_scroll=True)]
    ]

    right_input_layout = [
        [sg.Button("add selected to Title", size=(40, 1), key="-ADD TITLE-")],
        [sg.Text("Title:")],
        [sg.Input("", size=(40, 1), key="-TITLE INP-")],
        [sg.Button("Save Change", size=(40, 1), key="-SAVE CHANGE-")],
        [sg.Text("Changed Titles:")],
        [sg.Listbox(values=[], size=(40, 18),
                    enable_events=True, key="-CH TITLE BOX-", horizontal_scroll=True)],
        [sg.Button("Manage", key="-CH MANAGE-", size=(40, 1))]
    ]

    sub_Column_layout = [
        [
            sg.Text("Current Title:"),
            sg.Text("", key="-CUR TITLE TX-")
        ],
        [
            sg.Text("Current ID:"),
            sg.Text("", key="-CUR TITLE ID-"),
            sg.Button("Open Link", key="-OPEN WEB-")
        ],
        [
            sg.Input("", enable_events=True,
                     key="-CUR TITLE-", font=("Courier New", 18)),
            sg.Button("Coppy to Clippboard", key="-COPPY CLP-", pad=(0, 0)),
            sg.Button("AR", size=(6, 1), pad=(0, 0), key="-AR-")
        ],
        [
            sg.Column(left_input_layout),
            sg.Column(b2_layout),
            sg.Column(right_input_layout)
        ],
        [sg.VPush()]
    ]

    layout = [
        [
            sg.Column(title_layout),
            sg.Column(b1_layout),
            sg.Column(sub_Column_layout)
        ],
        [sg.Button("Download", key="-DL-", size=(140, 2))]
    ]

    def copySelected():
        try:
            selection = window["-CUR TITLE-"].Widget.selection_get()
        except:
            selection = ""
        return selection

    def getTitleData(data):
        titlesArr = []
        IDsArr = []
        for title in data:
            titlesArr.append(data[title]["title"])
            IDsArr.append(data[title]["videoID"])
        return titlesArr, IDsArr

    def updateAllBoxes():
        titlesArr, _ = getTitleData(titlesData)
        changedArr, _ = getTitleData(changedData)
        skippedArr, _ = getTitleData(skippedData)

        window["-TITLES BOX-"].update(titlesArr)
        window["-CH TITLE BOX-"].update(changedArr)
        window["-SK TITLE BOX-"].update(skippedArr)

    def loadNextTitle(Data, Array, ID, selectedNumber):

        window["-CUR TITLE TX-"].update(Array[selectedNumber][:75])
        window["-CUR TITLE ID-"].update(ID[selectedNumber])
        window["-CUR TITLE-"].update(Array[selectedNumber])
        window["-ARTIST INP-"].update(Data[ID[selectedNumber]]["newtitle"])
        window["-TITLE INP-"].update(Data[ID[selectedNumber]]["newartist"])

    def moveTitles(oldData, newData, titleID):
        singleTitle = oldData[titleID]
        ID = singleTitle["videoID"]
        newData[ID] = singleTitle
        del oldData[titleID]
        updateAllBoxes()

    # write all titles to titles.json
    playlists = json.load(open("items/" + folderName + "/config.json"))
    playlistsArr = []
    for x in range(len(playlists["playlists"])):
        playlistsArr.append(playlists["playlists"][x][1])

    youtube = googleapiclient.discovery.build(
        apiName, apiVersion, developerKey=apiKey)

    if "titles.json" not in os.listdir("items/" + folderName):
        titlesOutput = {}
        for playlistID in playlistsArr:
            requestContent = youtube.playlistItems().list(
                part="id, snippet", playlistId=playlistID, maxResults=50)

            responseC = requestContent.execute()

            titlesAmount = len(responseC["items"])
            for index in range(titlesAmount):
                videoID = responseC["items"][index]["snippet"]["resourceId"]["videoId"]
                videoTitle = responseC["items"][index]["snippet"]["title"]

                subTitle = {}
                subTitle["videoID"] = videoID
                subTitle["title"] = videoTitle
                subTitle["newtitle"] = ""
                subTitle["newartist"] = ""
                titlesOutput[videoID] = subTitle

            if "nextPageToken" in responseC:
                nextpageToken = responseC["nextPageToken"]
                while True:

                    requestCNT = youtube.playlistItems().list(
                        part="id, snippet", playlistId=playlistID,  maxResults=50,   pageToken=nextpageToken)
                    responseCNT = requestCNT.execute()

                    titlesAmount = len(responseCNT["items"])
                    for index in range(titlesAmount):
                        videoID = responseCNT["items"][index]["snippet"]["resourceId"]["videoId"]
                        videoTitle = responseCNT["items"][index]["snippet"]["title"]

                        subTitle = {}
                        subTitle["videoID"] = videoID
                        subTitle["title"] = videoTitle
                        subTitle["newtitle"] = ""
                        subTitle["newartist"] = ""
                        titlesOutput[videoID] = subTitle

                    if "nextPageToken" in responseCNT:
                        nextpageToken = responseCNT["nextPageToken"]
                    else:
                        break

        for title in list(titlesOutput):
            if titlesOutput[title]["title"] == "Private video" or titlesOutput[title]["title"] == "Deleted video":
                del titlesOutput[title]

        with open("items/" + folderName + "/titles.json", "w") as writeFile:
            json.dump(titlesOutput, writeFile, indent=4,
                      separators=(", ", ": "), sort_keys=False)

    # setting window Title to playlists
    configData = json.load(open(config_json))
    window = sg.Window(folderName, layout, finalize=True)
    skippedData = json.load(open(skipped_json))
    changedData = json.load(open(changed_json))
    titlesData = json.load(open(titles_json))
    loadedTitle = {}
    # add first Title
    if len(list(titlesData)) != 0:
        titlesArr, titlesID = getTitleData(titlesData)
        loadNextTitle(titlesData, titlesArr, titlesID, 0)
        curTitleID = titlesID[0]
        moveTitles(titlesData, loadedTitle, curTitleID)
    else:
        curTitleID = None

    titlesArr, titlesID = getTitleData(titlesData)
    changedArr, changedID = getTitleData(changedData)
    skippedArr, skippedID = getTitleData(skippedData)

    window["-TITLES BOX-"].update(titlesArr)
    window["-CH TITLE BOX-"].update(changedArr)
    window["-SK TITLE BOX-"].update(skippedArr)

    titleSelectedT = 0  # Index of the title that is selected in Titles
    titleSelectedC = 0  # Index of the title that is selected in Changed Titles
    titleSelectedS = 0  # Index of the title that is selected in Skipped Titles
    insertFirst = False  # Disable inserting a new Title when Titles is not empty

    while True:
        titlesArr, titlesID = getTitleData(titlesData)
        changedArr, changedID = getTitleData(changedData)
        skippedArr, skippedID = getTitleData(skippedData)

        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-ADD ARTIST-":
            window["-ARTIST INP-"].update(copySelected())

        if event == "-ADD TITLE-":
            window["-TITLE INP-"].update(copySelected())

        # opens the current title in webbrowser
        if event == "-OPEN WEB-":
            wbopen("https://www.youtube.com/watch?v=" +
                   loadedTitle[curTitleID]["videoID"])

        if event == "-COPPY CLP-" and len(titlesArr) != 0:
            copy(titlesData[curTitleID]["title"])

        if event == "-AR-":
            for title in list(titlesData):
                try:
                    ARartist, ARtitle = get_artist_title(
                        titlesData[title]["title"])
                    for character in ARartist:
                        if character in forbiddenCharacters:
                            ARartist = ARartist.replace(character, "")
                            print(character, ARartist)
                    for character in ARtitle:
                        if character in forbiddenCharacters:
                            ARtitle = ARtitle.replace(character, "")
                            print(character, ARtitle)

                    titlesData[title]["newtitle"] = ARtitle
                    titlesData[title]["newartist"] = ARartist

                    moveTitles(titlesData, changedData, title)
                except:
                    pass

        # Handle moving Titles between Boxes
        if event == "-TITLES BOX-" and len(titlesArr) != 0:
            titleSelectedT = titlesArr.index(str(values[event])[2:-2])

        if event == "-CH TITLE BOX-" and len(changedArr) != 0:
            titleSelectedC = changedArr.index(str(values[event])[2:-2])

        if event == "-SK TITLE BOX-" and len(skippedArr) != 0:
            titleSelectedS = skippedArr.index(str(values[event])[2:-2])

        if event == "-M CS-" and len(changedArr) != 0:
            selectedTitleIDC = changedID[titleSelectedC]
            moveTitles(changedData, skippedData, selectedTitleIDC)
            titleSelectedC = 0

        if event == "-M SC-" and len(skippedArr) != 0:
            selectedTitleIDS = skippedID[titleSelectedS]
            moveTitles(skippedData, changedData, selectedTitleIDS)
            titleSelectedS = 0

        if event == "-M ST-" and len(skippedArr) != 0:
            if len(titlesArr) == 0:
                insertFirst = True
            selectedTitleIDS = skippedID[titleSelectedS]
            moveTitles(skippedData, titlesData, selectedTitleIDS)
            titleSelectedS = 0
            titlesArr, titlesID = getTitleData(titlesData)
            if len(titlesArr) != 0 and insertFirst == True:
                loadNextTitle(titlesData, titlesArr, titlesID, 0)
                titlesArr, titlesID = getTitleData(titlesData)
                curTitleID = titlesID[0]
                insertFirst = False

        if event == "-CH MANAGE-":
            managedData = overview_GUI(changedData)
            if managedData != None:
                changedData = managedData

        if event == "-M TS-" and len(titlesArr) != 0:
            selectedTitleIDT = titlesID[titleSelectedT]
            moveTitles(titlesData, skippedData, selectedTitleIDT)
            if curTitleID == titlesID[titleSelectedT]:
                window["-CUR TITLE TX-"].update("-")
                window["-CUR TITLE ID-"].update("-")
                window["-CUR TITLE-"].update("")
                window["-TITLE INP-"].update("")
                window["-ARTIST INP-"].update("")
                titlesArr, titlesID = getTitleData(titlesData)
                if len(titlesID) != 0:
                    curTitleID = titlesID[0]
                else:
                    curTitleID = None
                loadNextTitle(titlesData, titlesArr, titlesID, titleSelectedT)
            titleSelectedT = 0

        if event == "-MA ST-" and len(skippedArr) != 0:
            if len(titlesArr) == 0:
                insertFirst = True
            while len(skippedID) != 0:
                selectedTitleIDS = skippedID[0]
                moveTitles(skippedData, titlesData, selectedTitleIDS)
                _, skippedID = getTitleData(skippedData)
            titlesArr, titlesID = getTitleData(titlesData)
            if len(titlesArr) != 0 and insertFirst == True:
                loadNextTitle(titlesData, titlesArr, titlesID, 0)
                moveTitles(titlesData, loadedTitle, titlesID[0])
                if len(titlesID) != 0:
                    curTitleID = titlesID[0]
                else:
                    curTitleID = None
                insertFirst = False

        if (event == "-SAVE CHANGE-" or event == "-TITLE SKIP-"):
            curTitleArtist = values['-ARTIST INP-']
            curTitleTitle = values['-TITLE INP-']

            if event == "-SAVE CHANGE-" and curTitleID != None:
                # add title with changed Title and Author to changed.json
                loadedTitle[curTitleID]["newtitle"] = curTitleTitle
                loadedTitle[curTitleID]["newartist"] = curTitleArtist
                moveTitles(loadedTitle, changedData, curTitleID)
            elif event == "-TITLE SKIP-" and curTitleID != None:
                # add title with changed Title and Author to changed.json
                moveTitles(loadedTitle, skippedData, curTitleID)

            titlesArr, titlesID = getTitleData(titlesData)
            # add next Title
            if len(titlesArr) >= 1:
                loadNextTitle(titlesData, titlesArr, titlesID, titleSelectedT)
                curTitleID = titlesID[titleSelectedT]
                moveTitles(titlesData, loadedTitle, curTitleID)
            else:
                window["-CUR TITLE TX-"].update("-")
                window["-CUR TITLE ID-"].update("-")
                window["-CUR TITLE-"].update("")
                window["-TITLE INP-"].update("")
                window["-ARTIST INP-"].update("")
                curTitleID = None
            # resetting selected Title
            titleSelectedT = 0

        if event == "-DL-":
            error = False
            if len(list(changedData)) == 0:
                error = "there are no titles to Download!"
            for title in list(changedData):
                if changedData[title]["newtitle"] == "":
                    error = "some Songs have no title assigned!"
                elif changedData[title]["newartist"] == "":
                    error = "some Songs have no artist assingen!"

            if error != False:
                errorWindow(error)
            else:
                window.close()
                return folderName, changedData

    with open("items/" + folderName + "/changed.json", "w") as writeFile:
        json.dump(changedData, writeFile, indent=4,
                  separators=(", ", ": "), sort_keys=False)

    with open("items/" + folderName + "/skipped.json", "w") as writeFile:
        json.dump(skippedData, writeFile, indent=4,
                  separators=(", ", ": "), sort_keys=False)

    with open("items/" + folderName + "/titles.json", "w") as writeFile:
        json.dump(titlesData, writeFile, indent=4,
                  separators=(", ", ": "), sort_keys=False)
    window.close()


if __name__ == '__main__':
    main_GUI()
