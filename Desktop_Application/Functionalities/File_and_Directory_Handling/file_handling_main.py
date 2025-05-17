import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
import shutil
from PIL import Image
import zipfile
from openpyxl import load_workbook
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from pptx import Presentation
from openpyxl import Workbook
from reportlab.pdfgen import canvas
import win32com.client
from github import Github
import subprocess
import time  # For sorting by date

g = Github("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")

class FileNavigatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marcus Assist")
        
        # Set dark theme colors
        self.bg_color = "#1e1e1e"  # Dark background
        self.fg_color = "#ffffff"  # White text
        self.entry_bg = "#2e2e2e"  # Darker background for entry widgets
        self.button_bg = "#3e3e3e"  # Button background
        self.button_fg = "#ffffff"  # Button text color
        self.highlight_color = "#4e4e4e"  # Highlight color for buttons

        # Configure root window background
        self.root.configure(bg=self.bg_color)

        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window width and height
        window_width = 1200
        window_height = 800
        
        # Calculate position to start the window at the right edge of the screen
        position_top = 0  # Start at the top of the screen
        position_right = screen_width - window_width
        
        # Set the geometry of the window
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # Current working directory and initial navigation state
        self.current_directory = os.getcwd()
        self.history = [self.current_directory]

        # Attributes for copy/cut/paste
        self.copied_items = []  # List to store copied items
        self.is_cut_operation = False  # Initialize here

        # Label for current directory
        self.directory_label = tk.Label(
            root, text=f"Current Directory: {self.current_directory}", 
            anchor="w", fg=self.fg_color, bg=self.bg_color, font=("Arial", 12)
        )
        self.directory_label.pack(fill="x", padx=10, pady=10)

        # ScrolledText widget for displaying contents
        self.display_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, height=30, bg=self.entry_bg, fg=self.fg_color, 
            font=("Consolas", 12), insertbackground=self.fg_color
        )
        self.display_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.display_area.insert(tk.END, "Welcome! Use commands like 'open <item>' or 'home'.\n")
        self.display_area.config(state=tk.DISABLED)

        # Command entry for user input
        self.command_entry = tk.Entry(
            root, bg=self.entry_bg, fg=self.fg_color, font=("Arial", 12), 
            insertbackground=self.fg_color
        )
        self.command_entry.pack(fill="x", padx=10, pady=10)
        self.command_entry.bind("<Return>", self.execute_command)

        # Buttons for common actions
        self.button_frame = tk.Frame(root, bg=self.bg_color)
        self.button_frame.pack(fill="x", padx=10, pady=10)

        self.home_button = tk.Button(
            self.button_frame, text="Home", command=self.go_home, 
            bg=self.button_bg, fg=self.button_fg, font=("Arial", 12), 
            activebackground=self.highlight_color, activeforeground=self.fg_color
        )
        self.home_button.pack(side="left", padx=5)

        self.back_button = tk.Button(
            self.button_frame, text="Back", command=self.go_back, 
            bg=self.button_bg, fg=self.button_fg, font=("Arial", 12), 
            activebackground=self.highlight_color, activeforeground=self.fg_color
        )
        self.back_button.pack(side="left", padx=5)

        self.refresh_button = tk.Button(
            self.button_frame, text="Refresh", command=self.refresh, 
            bg=self.button_bg, fg=self.button_fg, font=("Arial", 12), 
            activebackground=self.highlight_color, activeforeground=self.fg_color
        )
        self.refresh_button.pack(side="left", padx=5)

        # Initial content display (list drives and pinned folders method should be defined elsewhere)
        self.display_contents(self.list_drives_and_pinned_folders(), "Available Drives and Folders:")
        
    def go_home(self):
        """Navigates to the home directory."""
        self.current_directory = os.getcwd()
        self.history = [self.current_directory]
        contents = self.list_drives_and_pinned_folders()
        self.display_contents(contents, "Available Drives and Folders:")
        self.update_directory_label()

    def refresh(self):
        """Refreshes the current directory view."""
        contents = self.list_directory_contents(self.current_directory)
        self.display_contents(contents, f"Contents of {self.current_directory}:")
        self.update_directory_label()

    def list_drives_and_pinned_folders(self):
        """Lists available drives and pinned folders."""
        drives = [f"{chr(letter)}:\\" for letter in range(65, 91) if os.path.exists(f"{chr(letter)}:\\")]
        pinned_folders = {
            "Desktop": str(Path.home() / "Desktop"),
            "Documents": str(Path.home() / "Documents"),
            "Downloads": str(Path.home() / "Downloads"),
            "Music": str(Path.home() / "Music"),
            "Videos": str(Path.home() / "Videos")
        }
        print("Pinned Folders:", pinned_folders)
        return {**{drive: drive for drive in drives}, **pinned_folders}

    def display_contents(self, contents, header):
        """Displays the contents of the current directory or available drives."""
        self.display_area.config(state=tk.NORMAL)
        self.display_area.delete(1.0, tk.END)
        self.display_area.insert(tk.END, f"{header}\n\n")
        self.contents_map = {}
        for index, (key, value) in enumerate(contents.items(), start=1):
            self.contents_map[str(index)] = value  # Map by number
            self.contents_map[key.lower()] = value  # Map by lowercase name for case-insensitive matching
            self.display_area.insert(tk.END, f"{index}. {key}\n")

        self.display_area.config(state=tk.DISABLED)

    def update_directory_label(self):
        """Updates the directory label."""
        self.directory_label.config(text=f"Current Directory: {self.current_directory}")

    def execute_command(self, event=None):
        """Handles user commands."""
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)  # Clear the input field
        self.handle_command(command)  # Process the command directly

    def handle_command(self, command):
        """Handles commands received from the WebSocket server."""
        # Clear existing input (if any)
        self.command_entry.delete(0, tk.END)

        if command.lower() == "home":
            self.go_home()
            return

        if command.lower().startswith("open "):
            target = command[5:].strip().lower()
            match = None
            # Try to match the target as a number or string
            for key, value in self.contents_map.items():
                if key.lower() == target or str(key).lower() == target or (target + ":\\") == value.lower():
                    match = value
                    break

            if not match:
                self.display_message(f"Invalid target: {target}")
                return

            if os.path.isdir(match):
                # Open folder
                self.history.append(match)
                self.current_directory = match
                os.chdir(match)
                contents = self.list_directory_contents(match)
                self.display_contents(contents, f"Contents of {match}:")
            elif os.path.isfile(match):
                # Open file
                self.display_message(f"Opening file: {match}")
                os.startfile(match)
            else:
                self.display_message(f"{match} is not accessible.")
            self.update_directory_label()

        elif command.lower().startswith("create folder"):
            folder_name = command[len("create folder"):].strip()  # Extract the part after "create folder" and strip extra spaces
            if folder_name:  # Check if the folder name is not empty
                self.create_folder(folder_name)
                
        elif command.lower().startswith("create"):
            parts = command.split(" ", 2)  # Split command into parts (file_type and file_name)
            if len(parts) < 3:
                self.display_message("Invalid command. Use: create <filetype> <filename>")
                return

            file_type = parts[1].strip().lower()
            file_name = parts[2].strip()

            if file_name:
                self.create_file(file_type, file_name)
            else:
                self.display_message("Please specify a valid file name.")
                
        elif command.lower().startswith("copy "):
            targets = command[len("copy "):].strip()  # Extract the part after "copy" and strip extra spaces
            if targets:
                self.copy_items(targets)  # Call the copy_item method

        elif command.lower() == "paste":
            self.paste_items()
            
        elif command.lower().startswith("cut"):
            # Extract the part after "cut" and strip extra spaces
            targets = command[len("cut"):].strip()
            if targets:  # Ensure targets are provided
                self.cut_items(targets)  # Call the cut function
        
        elif command.lower() == "go back":
            self.go_back()
            return
        
        elif command.lower().startswith("delete "):
            targets = command[len("delete "):].strip()
            if targets:
                self.delete_item(targets)
                self.display_message("deleted")
            else:
                self.display_message("Invalid format. Use: delete <file1, file2, folder1>")
                
        elif command.lower().startswith("rename "):
            parts = command[len("rename "):].split(" to ")
            if len(parts) == 2:
                target = parts[0].strip()
                new_name = parts[1].strip()
                if target and new_name:
                    self.rename_item(target, new_name)
                else:
                    self.display_message("Invalid format. Use: rename <no./name> to <new_name>")
                    
        elif command.lower().startswith("zip "):
            target = command[len("zip "):].strip()
            if target:
                self.zip_folder(target)
            else:
                self.display_message("Invalid format. Use: zip <folder_no./name>")

        elif command.lower().startswith("unzip "):
            zip_file = command[len("unzip "):].strip()
            if zip_file:
                self.unzip_folder(zip_file)
            else:
                self.display_message("Invalid format. Use: unzip <zip_no./name>")

        elif command.lower().startswith("convert "):
            self.convert_file(command[8:].strip())
            
        elif command.lower() == "push directory":
            self.push_to_repository()  # Call the push function when the user types this command
        
        elif command.lower() == "sort by date":
            self.sort_by_date()
        
        elif command.lower() == "sort by name":
            self.sort_by_name()
        
        elif command.lower() == "sort by size":
            self.sort_by_size()
        
        else:
            self.display_message(f"Unknown command: {command}")
                
        

    def list_directory_contents(self, directory):
        """Lists the contents of a directory."""
        try:
            contents = os.listdir(directory)
            return {item: os.path.join(directory, item) for item in contents}
        except PermissionError:
            self.display_message("Permission denied.")
            return {}
        
    def go_back(self):
        """Navigates to the previous directory in history."""
        if len(self.history) > 1:
            # Remove the current directory from history
            self.history.pop()
            # Set the previous directory as the current one
            self.current_directory = self.history[-1]
            os.chdir(self.current_directory)
            # Refresh the directory contents
            contents = self.list_directory_contents(self.current_directory)
            self.display_contents(contents, f"Contents of {self.current_directory}:")
            self.update_directory_label()
        else:
            self.display_message("No previous directory to go back to.")


    def create_folder(self, folder_name):
        """Creates a new folder in the current directory."""
        if not folder_name:
            self.display_message("Please specify a valid folder name.")
            return

        folder_path = os.path.join(self.current_directory, folder_name)
        try:
            os.makedirs(folder_path)
            self.display_message(f"Folder created: {folder_name}")
            # Update display to show the new folder
            contents = self.list_directory_contents(self.current_directory)
            self.display_contents(contents, f"Contents of {self.current_directory}:")
        except FileExistsError:
            self.display_message(f"Folder already exists: {folder_name}")
        except Exception as e:
            self.display_message(f"Error creating folder: {e}")
    
    def create_file(self, file_type, file_name):
        """Creates a file of the specified type and filename."""
        try:
            if file_type == "excel":
                if not file_name.endswith(".xlsx"):
                    file_name += ".xlsx"
                wb = Workbook()
                wb.save(file_name)
            elif file_type == "word":
                if not file_name.endswith(".docx"):
                    file_name += ".docx"
                doc = Document()
                doc.save(file_name)
            elif file_type == "ppt":
                if not file_name.endswith(".pptx"):
                    file_name += ".pptx"
                ppt = Presentation()
                ppt.save(file_name)
            elif file_type == "document":
                if not file_name.endswith(".txt"):
                    file_name += ".txt"
                with open(file_name, "w") as f:
                    f.write("")  # Create an empty file
            else:
                self.display_message(f"Unsupported file type: {file_type}")
                return

            self.display_message(f"Created file: {file_name}")
             # Refresh directory contents after file creation
            contents = self.list_directory_contents(self.current_directory)
            self.display_contents(contents, f"Contents of {self.current_directory}:")
        except Exception as e:
            self.display_message(f"Failed to create file: {e}")
    
    def copy_items(self, target):
        """Handles the copy command for multiple items."""
        targets = self.get_items_from_command(target)
        if targets:
            self.copied_items.extend(targets)  # Use extend to add multiple items
            self.is_cut_operation = False
            self.display_message(f"Copied: {', '.join(os.path.basename(item) for item in targets)}")

    def cut_items(self, target):
        """Handles the cut command for multiple items."""
        targets = self.get_items_from_command(target)
        if targets:
            self.copied_items.extend(targets)  # Use extend to add multiple items
            self.is_cut_operation = True
            self.display_message(f"Cut: {', '.join(os.path.basename(item) for item in targets)}")

    def paste_items(self):
        """Handles the paste command."""
        if not self.copied_items:
            self.display_message("No items to paste. Use 'copy' or 'cut' first.")
            return

        try:
            for item in self.copied_items:
                source_path = item
                target_path = os.path.join(self.current_directory, os.path.basename(item))

                if self.is_cut_operation:
                    shutil.move(source_path, target_path)
                else:
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, target_path)
                    else:
                        shutil.copy2(source_path, target_path)

            self.copied_items = []
            self.is_cut_operation = False
            contents = self.list_directory_contents(self.current_directory)
            self.display_contents(contents, f"Contents of {self.current_directory}:")
            self.display_message("Paste operation completed.")
        except Exception as e:
            self.display_message(f"Failed to paste items: {e}")

    def get_items_from_command(self, target):
        """Fetches items specified in the command, supports comma-separated list."""
        target_items = [item.strip() for item in target.split(",")]  # Split by comma and strip spaces
        matches = []
        for t in target_items:
            match = [value for key, value in self.contents_map.items() if key.lower() == t.lower() or str(key).lower() == t.lower()]
            if match:
                matches.extend(match)
            else:
                self.display_message(f"Invalid target: {t}")
        return matches
     
    def delete_item(self, targets):
        """Deletes multiple files or folders from the current directory."""
        target_list = [target.strip() for target in targets.split(",")]

        deleted_items = []
        failed_items = []

        for target in target_list:
            match = next((value for key, value in self.contents_map.items()
                          if key.lower() == target or target == str(key)), None)
            if not match:
                failed_items.append(target)
                continue

            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)  # Remove folder and its contents
                elif os.path.isfile(match):
                    os.remove(match)  # Remove file
                else:
                    failed_items.append(target)
                    continue

                deleted_items.append(os.path.basename(match))
            except Exception as e:
                failed_items.append(target)
                self.display_message(f"Error deleting {target}: {e}")

        # Display success message
        if deleted_items:
            self.display_message(f"Deleted item(s): {', '.join(deleted_items)}")

        # Display failed items
        if failed_items:
            self.display_message(f"Failed to delete item(s): {', '.join(failed_items)}")

        # Refresh directory contents
        contents = self.list_directory_contents(self.current_directory)
        self.display_contents(contents, f"Contents of {self.current_directory}:")
    
    def rename_item(self, target, new_name):
        """Renames a file or folder."""
        # Match the target by number or name
        match = next((value for key, value in self.contents_map.items()
                      if key.lower() == target or target == str(key)), None)

        if not match:
            self.display_message(f"Item '{target}' not found.")
            return

        # Get the current path and new path
        current_path = match
        new_path = os.path.join(self.current_directory, new_name)

        # Check if the new name already exists
        if os.path.exists(new_path):
            self.display_message(f"Cannot rename to '{new_name}' as it already exists.")
            return

        try:
            # Perform the renaming operation
            os.rename(current_path, new_path)
            self.display_message(f"Renamed '{os.path.basename(current_path)}' to '{new_name}'")
        except Exception as e:
            self.display_message(f"Error renaming item '{target}': {e}")

        # Refresh directory contents
        contents = self.list_directory_contents(self.current_directory)
        self.display_contents(contents, f"Contents of {self.current_directory}:")

    def zip_folder(self, target):
        """Zips a folder into a .zip archive with the same name and saves it in the current directory."""
        # Match the target by number or name
        match = next((value for key, value in self.contents_map.items()
                      if key.lower() == target or target == str(key)), None)

        if not match or not os.path.isdir(match):
            self.display_message(f"'{target}' is not a valid folder to zip.")
            return

        zip_name = os.path.basename(match)  # Use folder name for the zip file
        zip_path = os.path.join(self.current_directory, f"{zip_name}.zip")

        try:
            # Create the zip archive
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', match)
            self.display_message(f"Folder '{zip_name}' zipped as '{zip_name}.zip' in the current directory.")
        except Exception as e:
            self.display_message(f"Error zipping folder '{target}': {e}")

    def unzip_folder(self, zip_file):
        """Unzips a .zip file in the current directory with its original name as the output folder."""
        # Match the target by number or name
        match = next((value for key, value in self.contents_map.items()
                      if key.lower() == zip_file or zip_file == str(key)), None)

        if not match or not os.path.isfile(match) or not match.endswith('.zip'):
            self.display_message(f"'{zip_file}' is not a valid .zip file.")
            return

        folder_name = os.path.basename(match).replace('.zip', '')  # Use zip file name for output folder
        extract_path = os.path.join(self.current_directory, folder_name)

        try:
            # Extract the zip file
            with zipfile.ZipFile(match, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            self.display_message(f"'{os.path.basename(match)}' unzipped into folder '{folder_name}' in the current directory.")
        except Exception as e:
            self.display_message(f"Error unzipping file '{zip_file}': {e}")

    
    def convert_file(self, command):
        """Converts a file to the specified file type."""
        try:
            # Format should be "convert <filename> to pdf"
            parts = command.split(" to ")
            if len(parts) != 2 or parts[1].strip().lower() != "pdf":
                self.display_message("Invalid format. Use: convert <filename> to pdf")
                return

            filename = parts[0].strip()

            # Check if the file exists  
            file_to_convert = None
            for key, value in self.contents_map.items():
                if filename.lower() in key.lower() or filename.lower() in str(value).lower():
                    file_to_convert = value
                    break

            if not file_to_convert:
                self.display_message(f"No file found with the name: {filename}")
                return

            # Proceed with conversion
            if file_to_convert.endswith(".docx"):
                self.convert_word_to_pdf(file_to_convert)
            elif file_to_convert.endswith(".pptx"):
                self.convert_ppt_to_pdf(file_to_convert)
            elif file_to_convert.endswith(".xlsx"):
                self.convert_excel_to_pdf(file_to_convert)
            elif file_to_convert.lower().endswith(".txt"):
                self.convert_txt_to_pdf(file_to_convert)
            elif file_to_convert.lower().endswith((".jpg", ".jpeg", ".png")):
                self.convert_image_to_pdf(file_to_convert)
            else:
                self.display_message(f"Unsupported file type for conversion: {file_to_convert}")

        except Exception as e:
            self.display_message(f"Error during conversion: {str(e)}")

    def convert_word_to_pdf(self, filename):
        """Converts Word document to PDF."""
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(filename)
        pdf_filename = filename.replace(".docx", ".pdf")
        doc.SaveAs(pdf_filename, FileFormat=17)  # FileFormat=17 means PDF
        doc.Close()
        word.Quit()
        self.display_message(f"Word document converted to PDF: {pdf_filename}")

    def convert_ppt_to_pdf(self, filename):
        """Converts PowerPoint presentation to PDF."""
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        ppt = powerpoint.Presentations.Open(filename)
        pdf_filename = filename.replace(".pptx", ".pdf")
        ppt.SaveAs(pdf_filename, 32)  # 32 is for PDF format
        ppt.Close()
        powerpoint.Quit()
        self.display_message(f"PowerPoint presentation converted to PDF: {pdf_filename}")


    def convert_excel_to_pdf(self, filename):
        """Converts Excel file to PDF."""
        excel = win32com.client.Dispatch("Excel.Application")
        workbook = excel.Workbooks.Open(filename)
        pdf_filename = filename.replace(".xlsx", ".pdf")
        workbook.ExportAsFixedFormat(0, pdf_filename)  # 0 for PDF format
        workbook.Close()
        excel.Quit()
        self.display_message(f"Excel file converted to PDF: {pdf_filename}")

    def convert_txt_to_pdf(self, filename):
        """Converts Text file to PDF."""
        pdf_filename = filename.replace(".txt", ".pdf")
        c = canvas.Canvas(pdf_filename)
        with open(filename, 'r') as file:
            lines = file.readlines()
            y_position = 800  # Starting position on the PDF page
            for line in lines:
                c.drawString(100, y_position, line.strip())
                y_position -= 12
                if y_position < 40:  # New page after reaching bottom
                    c.showPage()
                    y_position = 800
        c.save()
        self.display_message(f"Text file converted to PDF: {pdf_filename}")
    
    def convert_image_to_pdf(self, filename):
        """Converts an image file to PDF."""
        try:
            image = Image.open(filename)
            pdf_filename = filename.rsplit(".", 1)[0] + ".pdf"
            image.convert("RGB").save(pdf_filename)
            self.display_message(f"Image converted to PDF: {pdf_filename}")
        except Exception as e:
            self.display_message(f"Error converting image to PDF: {e}")
    

    def push_to_repository(self):
        """Push files to an existing or new repository."""
        try:
            # Get the local directory path
            directory = self.current_directory  # Use current working directory from the app
            if not os.path.isdir(directory):
                self.display_message("Error: Invalid directory path.")
                return

            os.chdir(directory)
            # Check if the directory is already a Git repository
            if os.path.isdir(".git"):
                self.display_message("This directory is already a Git repository.")
                # Add, commit, and push changes
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Updated changes"], check=True)
                subprocess.run(["git", "push"], check=True)
                self.display_message("Changes pushed successfully.")
            else:
                self.display_message("This directory is not a Git repository.")
                # List repositories or create a new one
                repos = self.list_repositories()
                self.display_message("\nChoose an existing repository to push files:")
                print("0. Create a new repository")
                choice = int(input("Enter your choice (0 for new, or repo number): ").strip())

                if choice == 0:
                    # Create a new repository
                    repo = self.create_repository()
                    if not repo:
                        self.display_message("Failed to create a new repository. Exiting.")
                        return
                else:
                    # Use an existing repository
                    if 1 <= choice <= len(repos):
                        repo = repos[choice - 1]
                    else:
                        self.display_message("Invalid choice. Exiting.")
                        return

                # Initialize Git and push files
                with open("README.md", "w") as readme_file:
                    readme_file.write(f"# {repo.name}\n")
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
                subprocess.run(["git", "branch", "-M", "main"], check=True)
                subprocess.run(["git", "remote", "add", "origin", repo.clone_url], check=True)
                subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
                self.display_message(f"Successfully pushed the local directory to the repository '{repo.name}'.")
        except subprocess.CalledProcessError as e:
            self.display_message(f"Git operation failed: {e}")
        except Exception as e:
            self.display_message(f"Error pushing to repository: {e}")
        
    
    def display_message(self, message):
        """Displays a message in the text area."""
        self.display_area.config(state=tk.NORMAL)
        self.display_area.insert(tk.END, f"{message}\n")
        self.display_area.config(state=tk.DISABLED)

    def sort_by_date(self):
        """Sorts files and folders by modification date (descending)."""
        try:
            items = os.listdir(self.current_directory)
            items_with_dates = [(item, os.path.getmtime(os.path.join(self.current_directory, item))) for item in items]
            sorted_items = sorted(items_with_dates, key=lambda x: x[1], reverse=True)
            sorted_contents = {item[0]: os.path.join(self.current_directory, item[0]) for item in sorted_items}
            self.display_contents(sorted_contents, f"Contents of {self.current_directory} (Sorted by Date):")
        except Exception as e:
            self.display_message(f"Error sorting by date: {e}")

    def sort_by_name(self):
        """Sorts files and folders by name (descending)."""
        try:
            items = os.listdir(self.current_directory)
            sorted_items = sorted(items, reverse=True)
            sorted_contents = {item: os.path.join(self.current_directory, item) for item in sorted_items}
            self.display_contents(sorted_contents, f"Contents of {self.current_directory} (Sorted by Name):")
        except Exception as e:
            self.display_message(f"Error sorting by name: {e}")

    def sort_by_size(self):
        """Sorts files and folders by size (descending)."""
        try:
            items = os.listdir(self.current_directory)
            items_with_sizes = [(item, os.path.getsize(os.path.join(self.current_directory, item))) for item in items]
            sorted_items = sorted(items_with_sizes, key=lambda x: x[1], reverse=True)
            sorted_contents = {item[0]: os.path.join(self.current_directory, item[0]) for item in sorted_items}
            self.display_contents(sorted_contents, f"Contents of {self.current_directory} (Sorted by Size):")
        except Exception as e:
            self.display_message(f"Error sorting by size: {e}")