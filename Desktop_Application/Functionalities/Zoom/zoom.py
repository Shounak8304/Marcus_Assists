import pyautogui
import os
import time

# Define relative path for image
IMAGE_DIR = os.path.join(os.getcwd(), "Functionalities\\Zoom")  # Folder where image is stored
IMAGE_PATH = os.path.join(IMAGE_DIR, "1.png")  # Complete relative path
SECOND_IMAGE = os.path.join(IMAGE_DIR, "2.png")  # Second image to locate after 3 sec
JOIN_IMAGE = os.path.join(IMAGE_DIR, "3.png")  # Third image to locate after 3 sec


# List of common Zoom installation directories
COMMON_PATHS = [
    r"C:\Program Files\Zoom\bin\Zoom.exe",
    r"C:\Program Files (x86)\Zoom\bin\Zoom.exe",
    os.path.expanduser(r"~\AppData\Roaming\Zoom\bin\Zoom.exe"),  
    os.path.expanduser(r"~\Desktop\Zoom.lnk"),  
]

def find_zoom():
    """Search for Zoom executable"""
    for path in COMMON_PATHS:
        if os.path.exists(path):
            return path

    # Search entire C drive (optional but slow)
    for root, dirs, files in os.walk("C:\\"):
        for file in files:
            if file.lower() == "zoom.exe":
                return os.path.join(root, file)
    return None

def start_zoom_meeting():
    """Launch Zoom and start a new meeting"""
    zoom_path = find_zoom()

    if not zoom_path:
        print("Zoom application not found!")
        return

    print(f"Opening Zoom from: {zoom_path}")
    os.startfile(zoom_path)
    time.sleep(7)  # Wait for Zoom to fully open

    # Verify image path exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Image file not found: {IMAGE_PATH}")
        return

    # Locate and click the "New Meeting" button
    try:
        button_location = pyautogui.locateCenterOnScreen(IMAGE_PATH, confidence=0.8)
        if button_location:
            pyautogui.click(button_location)
            print("Started a new meeting.")
        else:
            print("Could not find the 'New Meeting' button on the screen. Try recapturing the image.")
    except Exception as e:
        print(f"Error locating 'New Meeting' button: {e}")
    
    time.sleep(7)

    #locate and click the "Join Meeting" button
    if not os.path.exists(SECOND_IMAGE):
        print(f"Image file not found: {SECOND_IMAGE}")
        return
    
    try:
        button_location = pyautogui.locateCenterOnScreen(SECOND_IMAGE, confidence=0.8)
        if button_location:
            pyautogui.click(button_location)
            print("Joining a meeting.")
        else:
            print("Could not find the 'Join Meeting' button on the screen. Try recapturing the image.")
    except Exception as e:
        print(f"Error locating 'Join Meeting' button: {e}")

def join_zoom_meeting():
    """Launch Zoom and join an existing meeting"""
    zoom_path = find_zoom()
    if not zoom_path:
        print("Zoom application not found!")
        return
    
    print(f"Opening Zoom from: {zoom_path}")
    os.startfile(zoom_path)
    time.sleep(7)  # Wait for Zoom to fully open

    # Verify image path exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Image file not found: {JOIN_IMAGE}")
        return

    # Locate and click the "Join Meeting" button
    try:
        button_location = pyautogui.locateCenterOnScreen(JOIN_IMAGE, confidence=0.8)
        if button_location:
            pyautogui.click(button_location)
            print("Joining a meeting.")
        else:
            print("Could not find the 'Join Meeting' button on the screen. Try recapturing the image.")
    except Exception as e:
        print(f"Error locating 'Join Meeting' button: {e}")


