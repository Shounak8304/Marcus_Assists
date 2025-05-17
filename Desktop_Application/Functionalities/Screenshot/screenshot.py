import os
from datetime import datetime
from PIL import ImageGrab  # Use Pillow's ImageGrab for screenshots

# Function to take a screenshot and save it in the Screenshots folder within Pictures
def take_screenshot():
    # Create a unique filename with a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"screenshot_{timestamp}.png"

    # Get the Screenshots folder in the default Pictures folder
    pictures_folder = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Screenshots')
    os.makedirs(pictures_folder, exist_ok=True)  # Ensure the Screenshots folder exists
    file_path = os.path.join(pictures_folder, filename)

    # Capture the screenshot using ImageGrab
    screenshot = ImageGrab.grab()

    # Save the screenshot
    screenshot.save(file_path)
    print(f"Screenshot saved as {file_path}")

