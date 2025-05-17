import os
import sys
import tkinter as tk
import customtkinter as ctk
import threading
import time
import subprocess
import ctypes
from vidstream import ScreenShareClient
import threading
import tkinter.messagebox as messagebox
from Functionalities.Startup_Login.startup import run_login
from Functionalities.GUI.Opening_Application_GUI.intro import play_video
from Functionalities.GUI.GUI_Icon.gui import run_icon_gui
from Functionalities.File_and_Directory_Handling.file_handling_main import FileNavigatorApp
from Functionalities.Client.client import websocket_in_background, server_connected_event, shutdown_application, set_command, get_command
from Functionalities.App_Opener.opener import launch_application
from Functionalities.Folder_Searcher.file_search import folder_searching
from Functionalities.Github_Automation.list_repositories import list_repositories_ui
from Functionalities.Github_Automation.create_repository import create_repository_ui
from Functionalities.Window_level_automation.window_level_automation import close_window, maximize_window, minimize_window, \
move_window_to_bottom_left,move_window_to_bottom_right, move_window_to_left_split,move_window_to_right_split,\
move_window_to_top_left,move_window_to_top_right,switch_desktop_next,switch_desktop_previous,switch_tab_next,\
switch_tab_previous,switch_window, copy_it, cut, paste, undo, redo, select_all, save, open_task_manager, open_settings,\
open_command_prompt
from Functionalities.Window_level_automation.window_list_automation import run_window_manager_gui
from Functionalities.Notes.Notes import sticky_notes_gui
from Functionalities.Youtube.youtube import search_youtube
from Functionalities.System_Status.Sys_Stat import show_system_status, close_system_status
from Functionalities.Google_Maps.open_maps import open_maps
from Functionalities.Email_Sender.impo_email import run_email_app
from Functionalities.Wifi.wifi import run_wifi_manager
from Functionalities.Scrolling.scrolling import start_scroll, stop_scroll
from Functionalities.Screenshot.screenshot import take_screenshot
from Functionalities.Youtube_Music.youtubemusic import play_music
from Functionalities.Money_Management.Money_Management import start_money_manager  # Import from Money_Management.py
from Functionalities.Spotify_Desktop.spotify import play_pause, next_track, previous_track
from Functionalities.Password_Manager.passwordmanager import run_password_manager
from Functionalities.Zoom.zoom import start_zoom_meeting, join_zoom_meeting
from Functionalities.Excel.excel import open_excel
from Functionalities.Email_Sender.emailhandler import EmailClientApp


latest_command = None  # Store latest command
directory_handler_thread = None  # Thread for directory_handler
directory_handler_window = None  # Reference to the directory_handler Tkinter window
is_navigation_active = False  # Track if navigation is active
window_manager_thread = None  # Thread for window manager
window_manager_window = None  # Reference to the window manager Tkinter window
is_window_manager_active = False  # Track if window manager is active
system_status_thread = None
system_status_window = None
system_status_active = False
money_management_thread = None
money_management_window = [None]  # Use a list to allow modification
money_management_active = [False]  # Use a list to allow modification
money_management_close_event = threading.Event()
password_manager_thread = None
password_manager_window = [None]
password_manager_active = [False]
password_manager_close_event = threading.Event()
excel_handler_thread = None
excel_handler_window = None
is_excel_active = False
email_client_window = None
email_client_thread = None
is_email_client_active = False


ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def keep_screen_alive_forever():
    """Runs in a separate thread to continuously keep the screen alive."""
    if os.name == 'nt':  # Windows
        while True:
            try:
                # Keep the display and system active
                result = ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
                )
                if result == 0:
                    print("⚠ Failed to keep screen awake on Windows.")
                # Sleep for a reasonable interval (e.g., 60 seconds) since the state persists
                time.sleep(60)
            except Exception as e:
                print(f"⚠ Error keeping screen awake on Windows: {e}")
                time.sleep(60)  # Avoid tight loop on failure
    else:
        print("⚠ Screen keeping is not supported on this OS.")


def start_icon_gui():
    """Starts floating GUI."""
    threading.Thread(target=run_icon_gui, daemon=True).start()

def start_directory_handler():
    """Starts the directory_handler GUI in a separate thread."""
    global directory_handler_window, is_navigation_active
    root = tk.Tk()
    directory_handler_window = FileNavigatorApp(root)
    
    try:
        root.mainloop()  # This will block the thread
    finally:

        print("🛑 Directory handler GUI closed.")
        is_navigation_active = False
        directory_handler_window = None

def start_window_manager():
    """Starts the window manager GUI in a separate thread."""
    global window_manager_window, is_window_manager_active
    root = ctk.CTk()
    window_manager_window = run_window_manager_gui(root)  # Pass root as an argument
    is_window_manager_active = True
    
    try:
        root.mainloop()  # This will block the thread
    finally:
        print("🛑 Window manager GUI closed.")
        is_window_manager_active = False
        window_manager_window = None

def run_system_status():
    global system_status_active, system_status_window
    system_status_window = show_system_status()  # Create the system status window
    system_status_active = True

    # Wait for the window to close
    while system_status_window.winfo_exists():
        system_status_window.update()  # Keep the window responsive
    print("🛑 System status GUI closed.")
    system_status_active = False
    system_status_window = None

def start_excel_handler():
    """Starts the Excel handler GUI in a separate thread."""
    global excel_handler_window, is_excel_active
    root = ctk.CTk()
    excel_handler_window = open_excel(root)
    
    try:
        root.mainloop()  # This will block the thread
    finally:
        print("🛑 Excel handler GUI closed.")
        is_excel_active = False
        excel_handler_window = None

def restart_system():
    """Restarts the operating system (requires administrative privileges)."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    if messagebox.askyesno("Confirm System Restart", "Are you sure you want to restart the system? This will close all applications."):
        print("⚠ Warning: Restarting the system will close all applications. Proceeding in 10 seconds...")
        time.sleep(10)  # Give the user some time to cancel
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
            elif os.name == 'posix':  # Linux/Unix
                subprocess.run(["sudo", "reboot"], check=True)
            else:
                print("❌ System restart not supported on this OS.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to restart system. Ensure you have administrative privileges. Error: {e}")
    else:
        print("🔙 System restart canceled by user.")
    root.destroy()


def start_email_client():
    """Starts the EmailClientApp GUI in a separate thread."""
    global email_client_window, is_email_client_active
    root = tk.Tk()
    email_client_window = EmailClientApp(root)
    is_email_client_active = True
    try:
        root.mainloop()  # Blocks the thread until the GUI closes
    except Exception as e:
        print(f"⚠ Error in email client thread: {e}")
    finally:
        is_email_client_active = False
        email_client_window = None
        print("🛑 Email client GUI closed.")


def main():
    """Main function to start Marcus."""
    global latest_command, directory_handler_thread, directory_handler_window, is_navigation_active,window_manager_thread,\
    window_manager_window, is_window_manager_active, system_status_thread, system_status_active, system_status_window,\
    money_management_thread, money_management_active, money_management_window, money_management_close_event, password_manager_active,\
    password_manager_thread, password_manager_window, password_manager_close_event, excel_handler_thread, is_excel_active,\
    excel_handler_window, email_client_window, email_client_thread, is_email_client_active

    threading.Thread(target=keep_screen_alive_forever, daemon=True).start()

    ctk.set_appearance_mode("dark") 
    ctk.set_default_color_theme("blue")  
    play_video()

    if run_login():
        websocket_thread = websocket_in_background()
        
        if not server_connected_event.wait(timeout=10):
            print("❌ Server connection failed. Exiting application.")
            shutdown_application()

        start_icon_gui()

        # Main loop to handle commands
        while True:
            command = get_command()
            if command:
                print(f"🔹 Latest Command in main: {command}")

                if command == "navigate" and not is_navigation_active:
                    # Start directory_handler in a separate thread
                    is_navigation_active = True
                    directory_handler_thread = threading.Thread(target=start_directory_handler, daemon=True)
                    directory_handler_thread.start()
                    print("🚀 Started directory handler.")             

                elif command == "close navigation" and is_navigation_active:
                    if directory_handler_window:
                        try:
                            if directory_handler_window.root.winfo_exists():  
                                directory_handler_window.root.quit()  # Gracefully quit Tkinter main loop
                                directory_handler_window.root.destroy()  # Destroy window completely
                        except Exception as e:
                            print(f"⚠ Error closing directory handler: {e}")

                    is_navigation_active = False
                    directory_handler_window = None

                    print("🛑 Stopped directory handler.")

                elif is_navigation_active:      
                    # Pass the command to the directory_handler GUI
                    if directory_handler_window and directory_handler_window.root.winfo_exists():
                        directory_handler_window.handle_command(command)
                    else:
                        print("⚠ Directory handler window is not available.")
                        is_navigation_active = False  # Reset flag if GUI is not available
                
                elif command == "process excel" and not is_excel_active:
                    # Start excel_handler in a separate thread
                    is_excel_active = True
                    excel_handler_thread = threading.Thread(target=start_excel_handler, daemon=True)
                    excel_handler_thread.start()
                    print("🚀 Started excel handler.")

                elif command == "close excel processing" and is_excel_active:
                    if excel_handler_window:
                        try:
                            if excel_handler_window.root.winfo_exists():
                                excel_handler_window.root.quit()
                                excel_handler_window.root.destroy()
                        except Exception as e:
                            print(f"⚠ Error closing excel handler: {e}")
                    
                    is_excel_active = False
                    excel_handler_window = None

                    print("🛑 Stopped excel handler.")
                
                elif is_excel_active:
                    # Pass the command to the excel_handler GUI
                    if excel_handler_window and excel_handler_window.root.winfo_exists():
                        excel_handler_window.handle_command(command)
                    else:
                        print("⚠ Excel handler window is not available.")
                        is_excel_active = False
                
                
                elif command == "list windows" and not is_window_manager_active:
                    # Start window manager in a separate thread
                    is_window_manager_active = True
                    window_manager_thread = threading.Thread(target=start_window_manager, daemon=True)
                    window_manager_thread.start()
                    print("🚀 Started window manager.")
                
                elif command == "close window listing" and is_window_manager_active:
                    if window_manager_window:
                        try:
                            if window_manager_window.root.winfo_exists():  
                                window_manager_window.root.quit()  # Gracefully quit Tkinter main loop
                                window_manager_window.root.destroy()  # Destroy window completely
                        except Exception as e:
                            print(f"⚠ Error closing window manager: {e}")

                    is_window_manager_active = False            
                    window_manager_window = None
                    print("🛑 Stopped window manager.")

                elif is_window_manager_active:
                    # Pass the command to the window manager GUI
                    if window_manager_window and window_manager_window.root.winfo_exists():
                        window_manager_window.handle_command(command)
                    else:
                        print("⚠ Window manager window is not available.")
                        is_window_manager_active = False  # Reset flag if GUI is not available
                
                elif command == "mailhandler" and not is_email_client_active:
                    is_email_client_active = True

                    email_client_thread = threading.Thread(target=start_email_client, daemon=True)
                    email_client_thread.start()
                    print("🚀 Started email client.")

                elif command == "close mailhandler" and is_email_client_active:
                    if email_client_window:
                        try:
                            if email_client_window.root.winfo_exists():
                                # Logout from email server before closing
                                if email_client_window.mail:
                                    email_client_window.mail.logout()
                                    print("Logged out from email server.")
                                email_client_window.root.quit()  # Gracefully quit Tkinter main loop
                                email_client_window.root.destroy()  # Destroy window completely
                        except Exception as e:
                            print(f"⚠ Error closing email client: {e}")
                    is_email_client_active = False
                    email_client_window = None
                    print("🛑 Stopped email client.")

                elif is_email_client_active:
                    if email_client_window and email_client_window.root.winfo_exists():
                        email_client_window.handle_command(command)
                    else:
                        print("⚠ Email client window is not available.")
                        is_email_client_active = False
                
                elif command == "system status" and not system_status_active:
                    system_status_thread = threading.Thread(target=run_system_status, daemon=True)
                    system_status_thread.start()
                    print("🚀 Started system status.")

                elif command == "close system status" and system_status_active:
                    try:
                        if system_status_window and system_status_window.winfo_exists():
                            close_system_status(system_status_window)  # Close the system status window
                    except Exception as e:
                        print(f"⚠ Error closing system status: {e}")
                    finally:
                        system_status_active = False
                        system_status_window = None
                
                elif command == "password manager" and not password_manager_active[0]:
                    password_manager_thread = threading.Thread(
                        target=run_password_manager,
                        args=(password_manager_active, password_manager_window, password_manager_close_event),
                        daemon=True
                    )
                    password_manager_thread.start()
                    print("🚀 Started password manager.")
                
                elif command == "close password manager" and password_manager_active[0]:
                    if password_manager_window[0] and password_manager_window[0].winfo_exists():
                        password_manager_close_event.set()
                        print("🛑 Signaled password manager to close.")
                    else:
                        password_manager_active[0] = False
                        password_manager_window[0] = None
                        print("🛑 Password manager already closed.")

                elif command == "money log" and not money_management_active[0]:
                    money_management_thread = threading.Thread(
                        target=start_money_manager,
                        args=(money_management_active, money_management_window, money_management_close_event),
                        daemon=True
                    )
                    money_management_thread.start()
                    print("🚀 Started money manager.")

                elif command == "close money log" and money_management_active[0]:
                    if money_management_window[0] and money_management_window[0].winfo_exists():
                        money_management_close_event.set()  # Signal the thread to close the window
                        print("🛑 Signaled money manager to close.")
                    else:
                        money_management_active[0] = False
                        money_management_window[0] = None
                        print("🛑 Money manager already closed.")
                    
                elif "open" in command and "app" in command:
                    # Extract the app name by removing "open" and "app"
                    app_name = command.replace("open", "").replace("app", "").strip()
                    # Call the function to launch the application
                    launch_application(app_name)
                
                elif "search" in command and "folder" in command:
                    # Extract the folder path by removing "search" and "folder"
                    folder_path = command.replace("search", "").replace("folder", "").strip()
                    folder_searching(folder_path)
                
                elif command == "list repository":
                    list_thread = threading.Thread(target=list_repositories_ui)
                    list_thread.start()
                
                elif command == "create repository":
                    create_thread = threading.Thread(target=create_repository_ui)
                    create_thread.start()
                
                elif command == "close window":
                    close_window()
                
                elif command == "maximize window":
                    maximize_window()
                
                elif command == "minimise window":
                    minimize_window()
                
                elif command == "left split":
                    move_window_to_left_split()
                
                elif command == "right split":
                    move_window_to_right_split()
                
                elif command == "bottom left split":
                    move_window_to_bottom_left()
                
                elif command == "bottom right split":
                    move_window_to_bottom_right()
                
                elif command == "top left split":
                    move_window_to_top_left()
                
                elif command == "top right split":
                    move_window_to_top_right()

                elif command == "switch tab next":
                    switch_tab_next()
                
                elif command == "switch tab previous":
                    switch_tab_previous()
                
                elif command == "switch window":
                    switch_window()
                
                elif command == "switch desktop next":
                    switch_desktop_next()
                
                elif command == "switch desktop previous":
                    switch_desktop_previous()

                elif command == "make a note":
                    sticky_notes_gui()

                elif "search" in command and "youtube" in command:
                    search_query = command.replace("search","").replace("youtube","").strip()
                    search_youtube(search_query)

                elif "direction to" in command:
                    direction_query = command.replace("direction to", "").strip()
                    open_maps(direction_query)
                
                elif command == "send email":
                    run_email_app()
                
                elif command == "wifi status":
                    run_wifi_manager()
                
                elif command == "scroll up":
                    start_scroll("up")

                elif command == "scroll down":
                    start_scroll("down")

                elif command == "stop scrolling":
                    stop_scroll()
                
                elif command == "take screenshot":
                    take_screenshot()

                elif command == "copy":
                    copy_it()
                
                elif command == "cut":
                    cut()
                
                elif command == "paste":
                    paste()
                
                elif command == "undo":
                    undo()
                
                elif command == "redo":
                    redo()
                
                elif command == "select all":
                    select_all()
                
                elif command == "save":
                    save()
                
                elif command == "open task manager":
                    open_task_manager()
                
                elif command == "open settings":
                    open_settings()

                elif command == "open command prompt":
                    open_command_prompt()

                elif "play" in command and "youtube music" in command:
                    # Extract the query by removing "play" and "music"
                    query = command.replace("play", "").replace("music", "").strip()
                    play_music(query)

                elif command == "play spotify":
                    play_pause()
                
                elif command == "play next":
                    next_track()
                
                elif command == "play previous":
                    previous_track()
                
                elif command == "start meeting":
                    start_zoom_meeting()
                
                elif command == "join meeting":
                    join_zoom_meeting()

                elif command == "restart desktop":
                    restart_system()
            
                elif command == "webshare desktop to android":
                    print("🔁 Starting screen share via FFmpeg...")
                    subprocess.Popen([
                        "ffmpeg",
                        "-f", "gdigrab",
                        "-framerate", "15",
                        "-i", "desktop",
                        "-vcodec", "libx264",
                        "-preset", "ultrafast",
                        "-f", "rtsp",
                        "rtsp://192.168.0.103:8554/live.stream"
                    ])

                elif command == "shutdown application":
                    # Shutdown the application
                    print("🛑 Shutting down Marcus...")
                    sys.exit(0)        

                else:
                    # Handle other commands (e.g., for other functionalities)
                    print(f"🔹 Handling other command: {command}")
                    # Add your logic here for other commands

if __name__ == "__main__":
    main()
