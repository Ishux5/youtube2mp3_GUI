import PySimpleGUI as sg
import json
import googleapiclient.discovery
import os
from error_GUI import errorWindow


def getAPIKEY(keyPath):
    with open(keyPath, 'r') as f:
        key = json.load(f)["apiKey"]
    return key


apiKey = getAPIKEY("credentials\credentials.json")
apiName = "youtube"
apiVersion = "v3"


def filterPL(data):
    PLArr, IDArr = [], []
    amount = len(data["items"])
    for pl in range(amount):
        PLArr.append(data["items"][pl]["snippet"]["title"])
        IDArr.append(data["items"][pl]["id"])
    return PLArr, IDArr


def selection_GUI():
    left_col = [
        [sg.Button("Open Playlists", size=(36, 1), key="-O PL-")],
        [
            sg.Text("Select Playlists"),
            sg.Text("", enable_events=True, key="-SEL PLID-")
        ],
        [sg.Listbox(values=[], size=(40, 10),
                    enable_events=True, key="-SEL PL BOX-")],
        [sg.Text("Added Playlists")],
        [sg.Listbox(values=[], size=(40, 10),
                    enable_events=True, key="-ADD PL BOX-")],
        [sg.Text("Name Save")],
        [sg.Input("", size=(40, 1), key="-SV NAME INP-")]
    ]

    right_col = [
        [sg.Text("Select Saves")],
        [sg.Listbox(values=[], size=(40, 27),
                    enable_events=True, key="-SEL SAVE-")]
    ]

    load_buttons = [
        [
            sg.Button("create new Save", size=(38, 1), key="-CR SAVE-"),
            sg.Button("load Save", size=(38, 1), key="-LD SAVE-")
        ]
    ]

    layout = [
        [
            sg.Column(left_col),
            sg.VSeparator(),
            sg.Column(right_col)
        ],
        [
            load_buttons
        ]
    ]
    window = sg.Window("Select Titles", layout, finalize=True)
    channelID = ""
    playlistArr, AddArr = [], []
    savesArr = next(os.walk("items"))[1]
    selBool = False
    if len(savesArr) == 0:
        selBool = True
    else:
        selSave = savesArr[0]
    while True:
        window["-SEL PL BOX-"].update(playlistArr)
        window["-ADD PL BOX-"].update(AddArr)
        window["-SEL SAVE-"].update(savesArr)
        event, value = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-SEL PL BOX-" and len(value["-SEL PL BOX-"]) != 0:
            playlistArr.remove(str(value["-SEL PL BOX-"])[2:-2])
            AddArr.append(str(value["-SEL PL BOX-"])[2:-2])

        if event == "-ADD PL BOX-" and len(value["-ADD PL BOX-"]) != 0:
            AddArr.remove(str(value["-ADD PL BOX-"])[2:-2])
            playlistArr.append(str(value["-ADD PL BOX-"])[2:-2])

        if event == "-SEL SAVE-":
            selSave = str(value["-SEL SAVE-"])[2:-2]

        if event == "-CR SAVE-":
            if value["-SV NAME INP-"] in savesArr:
                errorWindow("Save-Name already taken!")
            elif value["-SV NAME INP-"] == "":
                errorWindow("Save-Name is not allowed to be empty!")
            elif len(AddArr) == 0:
                errorWindow("No Playlists Selected!")
            else:
                path = "items/" + value["-SV NAME INP-"]
                os.makedirs(path)
                for x in ["/skipped.json", "/changed.json"]:
                    with open(path + x, "w") as writeFile:
                        json.dump({}, writeFile, indent=4, separators=(
                            ", ", ": "), sort_keys=False)
                config = {}
                config["channelID"] = channelID
                playlistTuples = []
                for x in AddArr:
                    names, ids = filterPL(responsePL)
                    index = names.index(x)
                    playlistID = ids[index]
                    PLTuple = (x, playlistID)
                    playlistTuples.append(PLTuple)
                config["playlists"] = playlistTuples
                with open(path + "/config.json", "w") as writeFile:
                    json.dump(config, writeFile, indent=4,
                              separators=(", ", ": "), sort_keys=False)

                with open("items/config.txt", "w") as f:
                    f.write(value["-SV NAME INP-"])

                break

        if event == "-LD SAVE-" and selBool == False:
            with open("items/config.txt", "w") as f:
                f.write(selSave)
            break
        elif event == "-LD SAVE-" and selBool == True:
            errorWindow("Create a Save before you select one!")

        if event == "-O PL-":
            channelID = openWindow(channelID)
            if channelID != None:
                try:
                    playlistArr, AddArr = [], []
                    youtube = googleapiclient.discovery.build(
                        apiName, apiVersion, developerKey=apiKey)
                    requestPL = youtube.playlists().list(
                        part="snippet, contentDetails",
                        channelId=channelID,
                        maxResults=25
                    )
                    responsePL = requestPL.execute()
                    window["-SEL PLID-"].update(channelID)
                    playlistArr, _ = filterPL(responsePL)
                except:
                    channelID = ""
                    window["-SEL PLID-"].update(channelID)
                    errorWindow("Invalid channelID")
            else:
                pass

    window.close()


def openWindow(curChannelID):
    layoutOpenPL = [
        [sg.Text("Input Channel ID:")],
        [sg.Input("", key="-O INP-")],
        [sg.Button("Done", key="-O DONE-")]
    ]

    window = sg.Window("Open Playlists", layoutOpenPL)

    while True:
        event, value = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED or (event == "-O DONE-" and value["-O INP-"] == ""):
            window.close()
            return None

        if event == "-O DONE-":
            if value["-O INP-"] == curChannelID:
                window.close()
            else:
                window.close()
                return value["-O INP-"]


if __name__ == '__main__':
    selection_GUI()
