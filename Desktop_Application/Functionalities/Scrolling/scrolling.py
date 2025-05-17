import pyautogui
import time
import threading

SCROLL_SPEED = 30  # Predefined scroll speed
is_scrolling = False
scroll_thread = None

def scroll(direction):
    """Continuously scroll in the given direction until stopped."""
    global is_scrolling
    is_scrolling = True
    while is_scrolling:
        pyautogui.scroll(SCROLL_SPEED if direction == "up" else -SCROLL_SPEED)
        time.sleep(0.001)

def start_scroll(direction):
    """Start scrolling in a separate thread to allow stopping and changing direction."""
    global scroll_thread, is_scrolling

    if is_scrolling:
        stop_scroll()  # Stop current scrolling before starting new one

    scroll_thread = threading.Thread(target=scroll, args=(direction,))
    scroll_thread.daemon = True
    scroll_thread.start()

def stop_scroll():
    """Stop scrolling."""
    global is_scrolling
    is_scrolling = False
    if scroll_thread:
        scroll_thread.join()

