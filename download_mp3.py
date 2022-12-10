from pytube import YouTube
import os
from pathlib import Path


def youtube2mp3(videoID, artist, title, path):
    yt = YouTube("https://youtu.be/" + videoID)

    # @ Extract audio with 160kbps quality from video
    video = yt.streams.filter(abr='160kbps').last()

    # @ Downloadthe file
    out_file = video.download(output_path=path)
    base, ext = os.path.splitext(out_file)
    new_file = Path(f'{path}\{artist} - {title}.mp3')
    os.rename(out_file, new_file)
    # @ Check success of download
    return videoID


if __name__ == '__main__':
    youtube2mp3("XXYlFuWEuKI", "The Weeknd", "Save Your Tears",
                "E:\Krims-Krams-Ecke D\OneDrive\Projekte\Programieren\Python\Playlist Downloader\python_downloads")
