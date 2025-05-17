import tkinter as tk
import customtkinter as ctk
import win32gui
import win32con
import win32process
import psutil  # To filter out system processes

class WindowManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Window Manager")
        self.root.geometry("400x300")
        
        self.windows = []
        self.selected_window = None

        self.create_widgets()
        self.update_window_list()

    def create_widgets(self):
        """Create GUI widgets."""
        self.window_listbox = ctk.CTkTextbox(self.root, width=300, height=200)
        self.window_listbox.pack(pady=10)

        self.close_button = ctk.CTkButton(self.root, text="Close Window", command=self.close_selected_window)
        self.close_button.pack(pady=5)

        self.refresh_button = ctk.CTkButton(self.root, text="Refresh List", command=self.update_window_list)
        self.refresh_button.pack(pady=5)

        self.open_button = ctk.CTkButton(self.root, text="Open Window", command=self.open_selected_window)
        self.open_button.pack(pady=5)

    def update_window_list(self):
        """Update the list of active windows."""
        self.windows = self.get_active_windows()
        self.window_listbox.delete(1.0, tk.END)
        for idx, window in enumerate(self.windows, start=1):
            self.window_listbox.insert(tk.END, f"{idx}. {window}\n")

    def get_active_windows(self):
        """Get a list of all active, visible, and non-minimized windows that appear in Alt+Tab."""
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                # Check if the window is a top-level window
                if win32gui.GetParent(hwnd) == 0:
                    # Check if the window is not minimized
                    placement = win32gui.GetWindowPlacement(hwnd)
                    if placement[1] != win32con.SW_SHOWMINIMIZED:
                        # Get the window title
                        window_title = win32gui.GetWindowText(hwnd)
                        if window_title:  # Only include windows with a title
                            # Get the process ID of the window
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                # Check if the process is a valid user process
                                process = psutil.Process(pid)
                                if process.status() != psutil.STATUS_ZOMBIE:  # Exclude zombie processes
                                    # Check if the window has a visible taskbar button (Alt+Tab requirement)
                                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                                    if not (ex_style & win32con.WS_EX_TOOLWINDOW):  # Exclude tool windows
                                        # Exclude specific system apps (e.g., Settings)
                                        if "Settings" not in window_title:
                                            windows.append(window_title)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                # Skip system or inaccessible processes
                                pass
        win32gui.EnumWindows(callback, None)
        return windows

    def close_selected_window(self):
        """Close the selected window."""
        if self.selected_window is not None:
            try:
                # Close the window by title (Windows-specific)
                hwnd = win32gui.FindWindow(None, self.selected_window)
                if hwnd:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                self.update_window_list()
            except Exception as e:
                print(f"Error closing window: {e}")

    def open_selected_window(self):
        """Open the selected window by name or number."""
        if self.selected_window is not None:
            try:
                # Open the window by title (Windows-specific)
                hwnd = win32gui.FindWindow(None, self.selected_window)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                print(f"Error opening window: {e}")

    def handle_command(self, command):
        """Handle commands from the main application."""
        if command.startswith("close"):
            # Handle commands like "close 1" or "close Netflix"
            if command.replace("close", "").strip().isdigit():
                # Close by number
                window_number = int(command.replace("close", "").strip())
                if 1 <= window_number <= len(self.windows):
                    self.selected_window = self.windows[window_number - 1]
                    self.close_selected_window()
            else:
                # Close by name
                window_name = command.replace("close", "").strip()
                for window in self.windows:
                    if window_name.lower() in window.lower():
                        self.selected_window = window
                        self.close_selected_window()
                        break
        elif command.startswith("open"):
            # Handle commands like "open 1" or "open Netflix"
            if command.replace("open", "").strip().isdigit():
                # Open by number
                window_number = int(command.replace("open", "").strip())
                if 1 <= window_number <= len(self.windows):
                    self.selected_window = self.windows[window_number - 1]
                    self.open_selected_window()
            else:
                # Open by name
                window_name = command.replace("open", "").strip()
                for window in self.windows:
                    if window_name.lower() in window.lower():
                        self.selected_window = window
                        self.open_selected_window()
                        break
        elif command == "refresh":
            self.update_window_list()

def run_window_manager_gui(root):
    """Start the Window Manager GUI."""
    app = WindowManagerApp(root)
    return app