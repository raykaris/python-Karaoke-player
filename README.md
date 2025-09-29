### Karaoke Lyrics Player

A Python-based karaoke application that plays audio from YouTube and displays synchronized lyrics in real-time.

## Features

- Extract audio from YouTube videos using yt-dlp.

- Display synchronized lyrics with timestamps.

- Fetch lyrics from LRCLib API, fallback to a local .lrc file.

- Real-time lyric highlighting in a Tkinter GUI.

- Playback controls: pause, resume, and skip lines.

## Requirements

- Python 3.8+

- VLC media player installed on your system

# Python packages:

- yt_dlp

- python-vlc

- tkinter (usually included with Python)

- requests

Install required packages using:
    ```
    pip install yt_dlp python-vlc requests
    ```

## Usage

1. Set the YouTube URL and track info at the top of player-2.py:
    ```
    YOUTUBE_URL = "https://youtu.be/LbLbkAMjPeM"
    TRACK_NAME = "Lonely"
    ARTIST_NAME = "Akon"
    LRC_FILE_PATH = "Lonely.lrc"
    ```

2. Run the script:
    ```
    python player-2.py
    ```

3. Controls in the GUI:

- Pause: Pause audio playback.

- Resume: Resume audio playback.

- Skip: Jump to the next line of lyrics.

## Lyrics Handling

- Attempts to fetch lyrics from the LRCLib API using track name and artist.

- Saves fetched lyrics to .lrc as a fallback.

- If API fails, reads lyrics from local .lrc file.

- Parses timestamps to synchronize lyrics with audio.

## Notes

- Ensure VLC is properly installed and accessible by Python.

- The app currently supports a single song at a time.

- For custom tracks, update YOUTUBE_URL, TRACK_NAME, and ARTIST_NAME.