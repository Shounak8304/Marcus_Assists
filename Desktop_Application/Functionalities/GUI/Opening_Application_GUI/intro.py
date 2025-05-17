import cv2
import pygame
import time
import threading
import numpy as np  # Import numpy for creating the black background

def play_audio():
    """Plays audio in a separate thread."""
    audio_path = "Functionalities\\GUI\\Opening_Application_GUI\\audio.mp3"
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

def play_video():
    """Plays video in fullscreen with synchronized audio for 5 seconds."""
    video_path = "Functionalities\\GUI\\Opening_Application_GUI\\Marcus.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1 / fps  # Time per frame in seconds

    # Start audio playback in a separate thread
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    # Get screen resolution
    screen_width = 1920  # Adjust to your screen resolution
    screen_height = 1080  # Adjust to your screen resolution

    cv2.namedWindow("Video Player", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video Player", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    start_time = time.time()  # Record the start time

    while cap.isOpened():
        frame_start_time = time.time()

        ret, frame = cap.read()
        if not ret:
            break  # Exit when video ends

        # Resize the frame to fit the screen while maintaining aspect ratio
        frame_height, frame_width = frame.shape[:2]
        aspect_ratio = frame_width / frame_height

        if aspect_ratio > (screen_width / screen_height):
            new_width = screen_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = screen_height
            new_width = int(new_height * aspect_ratio)

        resized_frame = cv2.resize(frame, (new_width, new_height))

        # Create a black background
        black_background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        # Calculate the position to place the resized frame on the black background
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2

        # Place the resized frame on the black background
        black_background[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_frame

        cv2.imshow("Video Player", black_background)

        # Check if 5 seconds have passed
        if time.time() - start_time >= 5:
            break

        # Calculate delay to maintain FPS
        elapsed_time = time.time() - frame_start_time
        delay = max(1, int((frame_time - elapsed_time) * 1000))  # Ensure correct FPS playback

        if cv2.waitKey(delay) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()  # Stop audio when video ends

