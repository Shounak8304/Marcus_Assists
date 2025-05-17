import tkinter as tk
from PIL import Image, ImageTk
import threading

# Function to process and return the image as square
def make_square_image(image_path, size=(40, 40)):
    img = Image.open(image_path).resize(size, Image.Resampling.LANCZOS)  # Resize to desired size
    return img

# Function to run the icon GUI
def run_icon_gui():
    # Create the main root window
    root = tk.Tk()
    root.overrideredirect(True)  # Remove title bar
    root.attributes("-topmost", True)  # Keep window on top
    root.geometry("40x40+0+0")  # Fix position at top-left corner (40x40 size at (0, 0))
    
    # Ensure transparency
    root.configure(bg='white')
    root.attributes("-transparentcolor", "white")  # Make white areas transparent
    
    # Process the image to make it square
    square_image = make_square_image("Functionalities\\GUI\\GUI_Icon\\2.png")  # Replace with your image path
    square_image_tk = ImageTk.PhotoImage(square_image)

    # Add the image to a label and ensure no padding or border
    icon_label = tk.Label(root, image=square_image_tk, bg="white", borderwidth=0, relief="flat")
    icon_label.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)  # No padding to avoid unwanted space
    
    # Keep a reference to the image to avoid garbage collection
    icon_label.image = square_image_tk

    # Run the GUI loop
    root.mainloop()

# Function to start the icon GUI in a thread-safe way
def start_icon_gui():
    # Run the GUI in the main thread
    threading.Thread(target=run_icon_gui, daemon=True).start()

# Example usage
if __name__ == "__main__":
    start_icon_gui()
    print("Main program continues to run...")