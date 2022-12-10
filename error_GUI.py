import PySimpleGUI as sg


def errorWindow(error_message):
    layout = [
        [sg.Text("ERROR!")],
        [sg.Text(error_message)]
    ]
    window = sg.Window("ERROR", layout)

    while True:
        event, _ = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()


if __name__ == '__main__':
    errorWindow("Test")
