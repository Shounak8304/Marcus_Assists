import os
import subprocess
import time
from AppOpener import open
import win32api
import win32con
from fuzzywuzzy import process
import keyboard

# Essential Desktop Apps
app_mapping = {
    "chrome": "Google Chrome",
    "firefox": "Mozilla Firefox",
    "edge": "Microsoft Edge",
    "vlc": "VLC Media Player",
    "notepad": "Notepad",
    "file explorer": "File Explorer",
    "task manager": "Task Manager",
    "calculator": "Calculator",
    "command prompt": "Command Prompt",
    "powershell": "PowerShell",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "outlook": "Microsoft Outlook",
    "teams": "Microsoft Teams"
}

def launch_application(app_name):
    def get_closest_match(app_name):
        match, score = process.extractOne(app_name, app_mapping.keys())
        return match if score > 80 else None

    def open_app(app_name):
        app_name_lower = app_name.lower()
        best_match = get_closest_match(app_name_lower)
        if best_match:
            try:
                open(app_mapping[best_match])
                print(f"Opening {app_mapping[best_match]}...")
            except Exception as e:
                print(f"Error opening app '{best_match}': {e}")
        else:
            print(f"App '{app_name}' not found in the list. Attempting to search for it...")
            search_and_open(app_name)

    def search_and_open(app_name):
        try:
            print("Pressing Windows key and searching for the app...")
            keyboard.press_and_release("win")
            time.sleep(0.5)
            keyboard.write(app_name)
            time.sleep(0.5)
            keyboard.press_and_release("enter")
            print(f"Opening {app_name}...")
        except Exception as e:
            print(f"Error during search: {e}")

    open_app(app_name)

if __name__ == "__main__":
    app_name = input("Enter the name of the app to open: ").strip()
    launch_application(app_name)
