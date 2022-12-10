import PySimpleGUI as sg
import json


def overview_GUI(data):
    def enterWindow(argument, currentArgument):
        layoutE = [
            [sg.Text(f"Current {argument}: {currentArgument}")],
            [sg.Text(f"Enter {argument}:")],
            [sg.Input("", key="-IN ARG-", enable_events=True)],
            [sg.Button("Done", key="-DONE E-")]
        ]
        windowE = sg.Window("Input", layoutE, finalize=True)

        while True:
            eventE, valueE = windowE.read()
            if eventE == "Exit" or eventE == sg.WIN_CLOSED:
                windowE.close()
                return ""
            if eventE == "-DONE E-":
                windowE.close()
                return valueE["-IN ARG-"]

    def createDataList(data):
        dlist = [[], [], [], []]
        for x in range(rows):
            title = list(data.keys())[x]
            dlist[0].append(data[title]["title"])
            dlist[1].append(data[title]["videoID"])
            dlist[2].append(data[title]["newartist"])
            dlist[3].append(data[title]["newtitle"])

        return dlist

    cols = 4
    rows = len(data)
    sg.set_options(font=('Courier New', 11))
    tableSize = [50, 12, 18, 28]

    dataList = createDataList(data)
    if rows > 38:
        minRow = rows
    else:
        minRow = 32

    listbox = [[sg.Listbox(dataList[i], size=(tableSize[i], minRow), pad=(0, 0), horizontal_scroll=True,
                           no_scrollbar=True, enable_events=True, key=f"listbox {i}") for i in range(cols)]]

    layout = [
        [
            sg.Text("Old Title".center(tableSize[0]), pad=(0, 0)),
            sg.Text("ID".center(tableSize[1]), pad=(0, 0)),
            sg.Text("new Artist".center(tableSize[2]), pad=(0, 0)),
            sg.Text("new Title".center(tableSize[3]), pad=(0, 0))
        ],
        [sg.Column(listbox, size=(1000, 600), pad=(0, 0), scrollable=True,
                   vertical_scroll_only=True)],
        [sg.Button("Done", size=(110, 0), key="-DONE-")]
    ]

    window = sg.Window("Overview", layout, finalize=True)

    while True:
        event, value = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            return None

        if event.startswith('listbox'):
            row = window[event].get_indexes()[0]
            user_event = False
            for i in range(cols):
                window[f'listbox {i}'].set_value([])
                window[f'listbox {i}'].Widget.selection_set(row)

            # edit new Artist
            if event == "listbox 2":
                accessMainWindow = False
                selectedID = dataList[1][row]
                enteredValue = enterWindow(
                    "Artist", data[selectedID]["newartist"])
                if enteredValue != "":
                    data[selectedID]["newartist"] = enteredValue
                    dataList = createDataList(data)
                    window["listbox 2"].update(dataList[2])

            # edit new title
            if event == "listbox 3":
                selectedID = dataList[1][row]
                enteredValue = enterWindow(
                    "Title", data[selectedID]["newtitle"])
                if enteredValue != "":
                    selectedID = dataList[1][row]
                    data[selectedID]["newtitle"] = enteredValue
                    dataList = createDataList(data)
                    window["listbox 3"].update(dataList[3])

        if event == "-DONE-":
            window.close()
            return data


if __name__ == '__main__':
    data = json.load(open("items\\Normal1\\changed.json"))

    datanew = overview_GUI(data)
    # print(datanew)
