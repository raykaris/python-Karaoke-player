import yt_dlp
import vlc
import tkinter as tk
from threading import Thread
import time
import requests
import re
import os

# === CONFIG ===
YOUTUBE_URL = "https://youtu.be/w4RXGsLyfXU"
TRACK_NAME = "Lonely"
ARTIST_NAME = "Akon"
LRCLIB_API_URL = f"https://lrclib.net/api/get?track_name={TRACK_NAME}&artist_name={ARTIST_NAME}"
LRC_FILE_PATH = "Lonely.lrc"  # Local .lrc fallback file

# === AUDIO FUNCTIONS ===
def get_audio_url(url):
    ydl_opts = {'format': 'bestaudio', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']

# === LYRICS FUNCTIONS ===
def get_synced_lyrics_api(track_name, artist_name):
    """Fetch lyrics from LRCLib API"""
    params = {"track": track_name, "artist": artist_name, "format": "json"}
    try:
        response = requests.get(LRCLIB_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()  
        else:
            print("LRCLib API returned status:", response.status_code)
            return None
    except Exception as e:
        print("LRCLib API error:", e)
        return None

def parse_lrc(lrc_path):
    """Parse local .lrc file into [{'timestamp':ms,'text':line}, ...]"""
    if not os.path.exists(lrc_path):
        return None
    pattern = re.compile(r"\[(\d+):(\d+\.\d+)\](.*)")
    lyrics = []
    with open(lrc_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                timestamp = int((minutes * 60 + seconds) * 1000)
                text = match.group(3).strip()
                lyrics.append({"timestamp": timestamp, "text": text})
    return lyrics

def get_lyrics(track_name, artist_name):
    """Try API first, fallback to .lrc file"""
    lyrics = get_synced_lyrics_api(track_name, artist_name)
    if lyrics:
        return lyrics
    print("Falling back to local .lrc file...")
    lyrics = parse_lrc(LRC_FILE_PATH)
    if lyrics:
        return lyrics
    exit("No lyrics available. Exiting.")

# === GUI & KARAOKE ===
class KaraokeApp:
    def __init__(self, root, lyrics, player):
        self.root = root
        self.lyrics = lyrics
        self.player = player

        self.text_widget = tk.Text(root, width=60, height=15, font=("Helvetica", 14))
        self.text_widget.pack(padx=10, pady=10)
        self.text_widget.tag_config("current", foreground="red")
        self.text_widget.config(state=tk.DISABLED)

        self.scroll_thread = Thread(target=self.scroll_lyrics)
        self.scroll_thread.daemon = True
        self.scroll_thread.start()

    def scroll_lyrics(self):
        for line in self.lyrics:
            timestamp = line['timestamp']
            lyric_text = line['text']
            while self.player.get_state() not in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                if self.player.get_time() >= timestamp:
                    break
                time.sleep(0.05)
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, lyric_text + '\n')
            self.text_widget.tag_remove("current", "1.0", tk.END)
            line_index = f"{self.text_widget.index('end').split('.')[0]}"
            start_index = f"{line_index}.0"
            end_index = f"{line_index}.end"
            self.text_widget.tag_add("current", start_index, end_index)
            self.text_widget.see(end_index)
            self.text_widget.config(state=tk.DISABLED)
            if self.player.get_state() in [vlc.State.Ended, vlc.State.Stopped, vlc.State.Error]:
                break

# === MAIN ===
if __name__ == "__main__":
    audio_url = get_audio_url(YOUTUBE_URL)
    if not audio_url:
        exit("Could not get audio URL. Exiting.")

    lyrics = get_lyrics(TRACK_NAME, ARTIST_NAME)

    player = vlc.MediaPlayer(audio_url)
    player.play()

    root = tk.Tk()
    root.title(f"Karaoke - {TRACK_NAME} by {ARTIST_NAME}")
    app = KaraokeApp(root, lyrics, player)
    root.mainloop()

    player.stop()
