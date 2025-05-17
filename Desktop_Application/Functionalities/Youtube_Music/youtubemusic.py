import webbrowser
import time
import urllib.parse
from ytmusicapi import YTMusic  # Install using: pip install ytmusicapi

def play_music(query):
    ytmusic = YTMusic()  # Initializes YouTube Music API
    search_results = ytmusic.search(query, filter="songs")  # Fetch only songs

    if not search_results:
        print("No results found.")
        return

    video_id = search_results[0]['videoId']  # Get the first result's video ID
    url = f"https://music.youtube.com/watch?v={video_id}&autoplay=1"
    
    print(f"Playing: {search_results[0]['title']} by {search_results[0]['artists'][0]['name']}")
    webbrowser.open(url)  # Opens the song in YouTube Music and autoplay starts


