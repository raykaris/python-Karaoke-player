import yt_dlp
import vlc
import tkinter as tk
from threading import Thread
import time
import requests
import re
import os

# === CONFIG ===
YOUTUBE_URL = "https://youtu.be/LbLbkAMjPeM"
TRACK_NAME = "Lonely"
ARTIST_NAME = "Akon"
# ALBUM_NAME = "Baldur's Gate 3 (Original Game Soundtrack)"
# DURATION = "233"
# LRCLIB_API_URL = f"https://lrclib.net/api/get?track_name={TRACK_NAME}&artist_name={ARTIST_NAME}&album_name={ALBUM_NAME}&duration={DURATION}"
LRC_FILE_PATH = "Lonely.lrc"

# === AUDIO FUNCTIONS ===
def get_audio_url(url):
    """Extract audio URL using yt-dlp Python module"""
    ydl_opts = {'format': 'bestaudio', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']

# === LYRICS FUNCTIONS ===
def get_synced_lyrics(track_name, artist_name):
    """Fetch synchronized lyrics using LRCLib API via HTTP requests"""
    url = "https://lrclib.net/api/get"
    params = {
        "track_name": track_name,
        "artist_name": artist_name,
        
        "format": "json"
        }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Access the correct key
            lyrics_data = data.get("lyrics")  # adjust if API returns a different key
            if not lyrics_data:
                return None
            lyrics = []
            for item in lyrics_data:
                lyrics.append({
                    "timestamp": item.get("timestamp", 0),
                    "text": item.get("text", "")
                })
            # save to .lrc for fallback
            with open(LRC_FILE_PATH, "w", encoding="utf-8") as f:
                for item in lyrics:
                    ms = item['timestamp']
                    minutes = int(ms // 60000)
                    seconds = (ms % 60000) / 1000
                    f.write(f"[{minutes}:{seconds:.2f}]{item['text']}\n")
            return lyrics
        else:
            print("Failed to fetch lyrics. Status:", response.status_code)
            return None
    except Exception as e:
        print("Error fetching lyrics:", e)
        return None
    
def parse_lrc(lrc_path):
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
    if not lyrics:
        # fallback: convert raw lines to dicts with 0 timestamp
        with open(lrc_path, "r", encoding="utf-8") as f:
            lyrics = [{"timestamp": 0, "text": line.strip()} for line in f if line.strip()]
    return lyrics

def get_lyrics(track_name, artist_name):
    """Try API first, fallback to .lrc file"""
    lyrics = get_synced_lyrics(track_name, artist_name)
    if lyrics:
        return lyrics
    print("Falling back to local .lrc file...")
    lyrics = parse_lrc(LRC_FILE_PATH)
    if lyrics:
        return lyrics
    exit("No lyrics available. Exiting.")

# === GUI ===
class KaraokeApp:
    def __init__(self, root, lyrics, player):
        self.root = root
        self.lyrics = lyrics
        self.player = player
        self.current_index = 0
        self.paused = False

        self.text_widget = tk.Text(root, width=60, height=10, font=("Helvetica", 14))
        self.text_widget.pack(padx=10, pady=10)
        self.text_widget.tag_config("current", foreground="red")
        self.text_widget.config(state=tk.DISABLED)

        controls_frame = tk.Frame(root)
        controls_frame.pack(pady=5)

        tk.Button(controls_frame, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Resume", command=self.resume).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Skip", command=self.skip).pack(side=tk.LEFT, padx=5)


        self.scroll_thread = Thread(target=self.scroll_lyrics)
        self.scroll_thread.daemon = True
        self.scroll_thread.start()

    def pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.paused = True

    def resume(self):
        if self.paused:
            self.player.play()
            self.paused = False

    def skip(self):
        """Skip to next line"""
        if self.current_index < len(self.lyrics) - 1:
            self.current_index += 1
            next_line = self.lyrics[self.current_index]
            self.player.set_time(next_line['timestamp'])

    def scroll_lyrics(self):
         while self.current_index < len(self.lyrics):
            if self.player.get_state() in [vlc.State.Ended, vlc.State.Error, vlc.State.Stopped]:
                break
            if self.paused:
                time.sleep(0.1)
                continue
            line = self.lyrics[self.current_index]
            timestamp = line.get('timestamp', 0)
            lyric_text = line.get('text', '')
            if self.player.get_time() >= timestamp:
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, lyric_text + '\n')
                self.text_widget.tag_remove("current", "1.0", tk.END)
                line_index = f"{self.text_widget.index('end').split('.')[0]}"
                start_index = f"{line_index}.0"
                end_index = f"{line_index}.end"
                self.text_widget.tag_add("current", start_index, end_index)
                self.text_widget.see(end_index)
                self.text_widget.config(state=tk.DISABLED)
                self.current_index += 1
            time.sleep(0.05)

# === MAIN ===
if __name__ == "__main__":
    audio_url = get_audio_url(YOUTUBE_URL)
    if not audio_url:
        exit("Could not get audio URL. Exiting.")

    lyrics = get_lyrics(TRACK_NAME, ARTIST_NAME)
    if not lyrics:
        print("Lyrics not available, using placeholder.")
        lyrics = [{"timestamp": 0, "text": "Lyrics not found."}]

    player = vlc.MediaPlayer(audio_url)
    player.play()

    root = tk.Tk()
    root.title(f"Karaoke - {TRACK_NAME} by {ARTIST_NAME}")
    app = KaraokeApp(root, lyrics, player)
    root.mainloop()

    player.stop()
