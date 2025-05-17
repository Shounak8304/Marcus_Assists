import pyautogui
import time
import os
import subprocess

# Function to check if Spotify is running
def is_spotify_open():
    try:
        # Check if Spotify process is running
        if os.name == "nt":  # For Windows
            output = subprocess.check_output(["tasklist"], text=True)
            return "Spotify.exe" in output
        else:  # For macOS/Linux
            output = subprocess.check_output(["ps", "-A"], text=True)
            return "Spotify" in output
    except Exception as e:
        print(f"Error checking if Spotify is open: {e}")
        return False

# Function to open Spotify in the background
def open_spotify():
    try:
        if os.name == "nt":  # For Windows
            # Use start with the /B flag to run in the background
            subprocess.Popen(["start", "/B", "spotify"], shell=True)
        elif os.name == "posix":  # For macOS/Linux
            if os.uname().sysname == "Darwin":  # macOS
                # Use open with -g to open in the background
                subprocess.Popen(["open", "-g", "-a", "Spotify"])
            else:  # Linux
                # Use nohup to run in the background
                subprocess.Popen(["nohup", "spotify", "&"])
        print("Spotify is now opening in the background...")
        time.sleep(5)  # Wait for Spotify to open
    except Exception as e:
        print(f"Error opening Spotify: {e}")

# Function to simulate keyboard shortcuts for Spotify
def play_pause():
    if not is_spotify_open():
            open_spotify()
            pyautogui.press('playpause')
    else:
        pyautogui.press('playpause')  # Simulates the Play/Pause media key

def next_track():
    pyautogui.press('nexttrack')  # Simulates the Next Track media key

def previous_track():
    pyautogui.press('prevtrack')  # Simulates the Previous Track media key

# Main function to prompt the user for input
