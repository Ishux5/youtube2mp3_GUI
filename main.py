from handle_select_GUI import selection_GUI
from handle_GUI import main_GUI
from download_GUI import download_GUI
from pathlib import Path


selection_GUI()
file, data = main_GUI()
path = str(Path().resolve()) + "\\items\\" + file
print(path)
download_GUI(data, path)
