import vlc
import time
import yt_dlp
import lyricsgenius
import json
import tkinter as tk
from threading import Thread

# === CONFIG ===
youtube_url = "https://youtu.be/6EEW-9NDM5k"
# Song Details
song_title = "Lonely"
artist_name = "Akon"
genius_api_token = ""

# === PLAYING YOUTUBE SONG ===
def get_audio_info(url):
    # Uses yt-dlp to excract audio
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', 'Unkown Title')
        duration = info.get('duration', 0)
        return audio_url, title, duration

def play_audio(url):
    # use VLC to play audio
    player = vlc.MediaPlayer(url)
    player.play()
    return player

# === FETCHING LYRICS ===
def get_lyrics(artist, title, token):
    genius = lyricsgenius.Genius(token)
    song = genius.search_song(title, artist)
    if song:
        lines = [line.strip() for line in song.lyrics.split("\n") if line.strip()]
        return lines
    return "Lyrics not found."

# === GUI ===
class KaraokeApp:
    def __init__(self, root, lyrics_lines, duration, player, song_title):
        self.root = root
        self.root.title(f"Karaoke - {song_title}")
        self.lyrics_lines = lyrics_lines
        self.duration = duration
        self.player = player

        self.text_widget = tk.Text(root, width=60, height=20, font=("Helvetica", 14))
        self.text_widget.pack(padx=10, pady=10)
        self.text_widget.tag_config("current", foreground="red")
        self.text_widget.config(state=tk.DISABLED)

        self.scroll_thread = Thread(target=self.scroll_lyrics)
        self.scroll_thread.daemon = True
        self.scroll_thread.start()
    
    def scroll_lyrics(self):
        interval = max(self.duration / len(self.lyrics_lines), 0.5)
        for idx, line in enumerate(self.lyrics_lines):
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, line + "\n")
            self.text_widget.tag_remove("current", "1.0", tk.END)
            # Highlight current line
            start_index = f"{idx + 1}.0"
            end_index = f"{idx + 1}.end"
            self.text_widget.tag_add("current", start_index, end_index)
            self.text_widget.see(end_index)
            self.text_widget.config(state=tk.DISABLED)
            time.sleep(interval)
            # Stop if song ends
            state = self.player.get_state()
            if str(state) in ["State.Ended", "State.Stopped", "State.Error"]:
                break

# === MAIN ===
if __name__ == "__main__":
    audio_url, video_title, duration = get_audio_info(youtube_url)
    if not audio_url:
        exit("Could not get url. Exiting")

    player = play_audio(audio_url)
    print(f"🎶 Now Playing: {video_title}")
    
    lyrics_lines = get_lyrics(artist_name, song_title, genius_api_token)
    
    root = tk.Tk()
    app = KaraokeApp(root, lyrics_lines, duration, player, video_title)
    root.mainloop()

    player.stop()