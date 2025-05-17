import pyautogui
import keyboard
import win32gui
import win32con

# Window management functions
def get_active_window():
    """Get the handle of the currently active window."""
    return win32gui.GetForegroundWindow()

def close_window(hwnd=None):
    """Close the specified window or the active window if no handle is provided."""
    if hwnd is None:
        hwnd = get_active_window()
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

def maximize_window():
    """Maximize the active window."""
    hwnd = get_active_window()
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def minimize_window():
    """Minimize the active window."""
    hwnd = get_active_window()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def move_window_to_left_split():
    """Move the active window to the left half of the screen."""
    pyautogui.hotkey('win', 'left')

def move_window_to_right_split():
    """Move the active window to the right half of the screen."""
    pyautogui.hotkey('win', 'right')

def move_window_to_top_left():
    """Move the active window to the top-left quadrant."""
    pyautogui.hotkey('win', 'left')
    pyautogui.hotkey('win', 'up')

def move_window_to_top_right():
    """Move the active window to the top-right quadrant."""
    pyautogui.hotkey('win', 'right')
    pyautogui.hotkey('win', 'up')

def move_window_to_bottom_left():
    """Move the active window to the bottom-left quadrant."""
    pyautogui.hotkey('win', 'left')
    pyautogui.hotkey('win', 'down')

def move_window_to_bottom_right():
    """Move the active window to the bottom-right quadrant."""
    pyautogui.hotkey('win', 'right')
    pyautogui.hotkey('win', 'down')

def switch_desktop_next():
    """Switch to the next virtual desktop."""
    pyautogui.hotkey('ctrl', 'win', 'right')

def switch_desktop_previous():
    """Switch to the previous virtual desktop."""
    pyautogui.hotkey('ctrl', 'win', 'left')

def switch_tab_next():
    """Switch to the next tab."""
    pyautogui.hotkey('ctrl', 'tab')

def switch_tab_previous():
    """Switch to the previous tab."""
    pyautogui.hotkey('ctrl', 'shift', 'tab')

def switch_window():
    """Switch between open windows using Alt+Tab."""
    pyautogui.hotkey('alt', 'tab')

def copy_it():
    """Copy the selected text or item."""
    pyautogui.hotkey('ctrl', 'c')

def cut():
    """Cut the selected text or item."""
    pyautogui.hotkey('ctrl', 'x')

def paste():
    """Paste the copied or cut text or item."""
    pyautogui.hotkey('ctrl', 'v')

def undo():
    """Undo the last action."""
    pyautogui.hotkey('ctrl', 'z')

def redo():
    """Redo the last undone action."""
    pyautogui.hotkey('ctrl', 'y')

def select_all():
    """Select all text or items."""
    pyautogui.hotkey('ctrl', 'a')

def save():
    """Save the current file or document."""
    pyautogui.hotkey('ctrl', 's')

def open_task_manager():
    """Open the task manager."""
    pyautogui.hotkey('ctrl', 'shift', 'esc')

def open_settings():
    """Open the Windows settings."""
    pyautogui.hotkey('win', 'i')

def open_command_prompt():
    """Open the command prompt."""
    pyautogui.hotkey('win', 'x')
    pyautogui.press('c')


# Register hotkeys
keyboard.add_hotkey("win+left", move_window_to_left_split)
keyboard.add_hotkey("win+right", move_window_to_right_split)
keyboard.add_hotkey("win+ctrl+left", move_window_to_top_left)
keyboard.add_hotkey("win+ctrl+right", move_window_to_top_right)
keyboard.add_hotkey("win+shift+left", move_window_to_bottom_left)
keyboard.add_hotkey("win+shift+right", move_window_to_bottom_right)
keyboard.add_hotkey("ctrl+win+left", switch_desktop_previous)
keyboard.add_hotkey("ctrl+win+right", switch_desktop_next)
keyboard.add_hotkey("ctrl+tab", switch_tab_next)
keyboard.add_hotkey("ctrl+shift+tab", switch_tab_previous)
keyboard.add_hotkey("alt+tab", switch_window)
keyboard.add_hotkey("ctrl+c", copy_it)
keyboard.add_hotkey("ctrl+x", cut)
keyboard.add_hotkey("ctrl+v", paste)
keyboard.add_hotkey("ctrl+z", undo)
keyboard.add_hotkey("ctrl+y", redo)
keyboard.add_hotkey("ctrl+a", select_all)
keyboard.add_hotkey("ctrl+s", save)
keyboard.add_hotkey("win+esc", open_task_manager)
keyboard.add_hotkey("win+i", open_settings)
keyboard.add_hotkey("win+x", lambda: pyautogui.press('c'))



