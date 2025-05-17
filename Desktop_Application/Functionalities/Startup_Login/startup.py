


#icon check rest all done - take others opinion once




import os
import json
import sys
import customtkinter as ctk
from tkinter import messagebox
from cryptography.fernet import Fernet
import re
from datetime import datetime

# Directory Setup
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(SAVE_DIR, exist_ok=True)

# File Paths
KEY_FILE = os.path.join(SAVE_DIR, "key.key")
USER_DATA_FILE = os.path.join(SAVE_DIR, "user_data.json")
LAST_LOGIN_FILE = os.path.join(SAVE_DIR, "last_login.json")

# Icon Paths (Relative to the script's location)
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Functionalities", "Startup_Login", "icon.ico")  # Main window icon
ICON_PHOTO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Functionalities", "Startup_Login", "icon.png")  # Child window icon

# Load or Generate Encryption Key
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

KEY = load_key()
cipher_suite = Fernet(KEY)

# Load User Data
def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump([], f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

# Save User Data
def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f)

# Authenticate User
def authenticate_user(username, password):
    user_data = load_user_data()
    for user in user_data:
        if user["username"] == username:
            try:
                decrypted_password = cipher_suite.decrypt(user["password"].encode()).decode()
                if decrypted_password == password:
                    return True
            except Exception:
                messagebox.showerror("Error", "Data corrupted or invalid key.")
                return False
    return False

# Save Last Login
def save_last_login(username):
    with open(LAST_LOGIN_FILE, "w") as f:
        json.dump({"last_login": username}, f)

# Load Last Login
def load_last_login():
    if os.path.exists(LAST_LOGIN_FILE):
        with open(LAST_LOGIN_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_login", None)
    return None

# Clear Last Login
def clear_last_login():
    if os.path.exists(LAST_LOGIN_FILE):
        os.remove(LAST_LOGIN_FILE)

# Validate Email
def validate_email(email):
    return re.match(r"[^@]+@gmail\.com", email) is not None

# Validate Phone Number
def validate_phone(phone):
    return re.match(r"^\d{10}$", phone) is not None

# Validate Password
def validate_password(password):
    return re.match(r"^\d{4}$", password) is not None

# Validate Username
def validate_username(username):
    return len(username) > 4 and username.isalnum()

# Main Login UI
def run_login():
    last_user = load_last_login()  # Check last login
    if last_user:  # Auto-login if last user exists
        def logout():
            clear_last_login()
            root.destroy()
            run_login()  # Restart login process
        
        root = ctk.CTk()
        root.title("Marcus Assists - Auto Login")
        root.geometry("400x250")

        # Set icon for the main window
        if os.path.exists(ICON_PATH):
            root.iconbitmap(ICON_PATH)

        frame = ctk.CTkFrame(root)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"Welcome back, {last_user}!", font=("Arial", 14)).pack(pady=20)
        
        ctk.CTkButton(frame, text="Logout", command=logout, fg_color="#d9534f").pack(pady=10)

        # Automatically close the welcome page after 5 seconds
        root.after(5000, root.destroy)  # Close window after 5 seconds
        root.mainloop()
        return True  # Auto-login success

    success = False  # Track login success
    
    def attempt_login():
        nonlocal success
        username = username_entry.get()
        password = password_entry.get()
        
        if authenticate_user(username, password):
            save_last_login(username)
            success_label.configure(text=f"Welcome, {username}!", text_color="lightgreen")  # Show success on GUI
            root.after(1000, root.destroy)  # Close window after 1 second
            success = True
        else:
            success_label.configure(text="Invalid credentials. Try again.", text_color="red")

    def open_signup_window():
        user_data = load_user_data()
        if len(user_data) >= 3:
            messagebox.showwarning("Limit Reached", "Only 3 users allowed.")
            return

        root.withdraw()  # Hide the login window
        signup_window = ctk.CTkToplevel()
        signup_window.title("Signup")
        signup_window.geometry("600x500")  # Increased window size for additional fields

        # Set icon for the child window
        if os.path.exists(ICON_PHOTO_PATH):
            icon_photo = ctk.CTkImage(light_image=ICON_PHOTO_PATH, dark_image=ICON_PHOTO_PATH, size=(32, 32))
            signup_window.iconphoto(False, icon_photo)

        # Create a scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(signup_window, width=550, height=450)
        scrollable_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(scrollable_frame, text="Signup", font=("Arial", 16)).pack(pady=10)

        # Username and Password
        ctk.CTkLabel(scrollable_frame, text="New Username:").pack(pady=5)
        new_username_entry = ctk.CTkEntry(scrollable_frame, width=200)
        new_username_entry.pack(pady=5)

        ctk.CTkLabel(scrollable_frame, text="New Password (4 digits):").pack(pady=5)
        new_password_entry = ctk.CTkEntry(scrollable_frame, show="*", width=200)
        new_password_entry.pack(pady=5)

        # Additional Fields
        ctk.CTkLabel(scrollable_frame, text="Full Name:").pack(pady=5)
        full_name_entry = ctk.CTkEntry(scrollable_frame, width=200)
        full_name_entry.pack(pady=5)

        ctk.CTkLabel(scrollable_frame, text="Gender:").pack(pady=5)
        gender_combobox = ctk.CTkComboBox(scrollable_frame, values=["Male", "Female"], width=200)
        gender_combobox.pack(pady=5)

        # Date of Birth (Dropdowns for day, month, year)
        ctk.CTkLabel(scrollable_frame, text="Date of Birth:").pack(pady=5)
        dob_frame = ctk.CTkFrame(scrollable_frame)
        dob_frame.pack(pady=5)

        # Day dropdown (1-31)
        day_combobox = ctk.CTkComboBox(dob_frame, values=[str(i).zfill(2) for i in range(1, 32)], width=80)
        day_combobox.pack(side="left", padx=5)

        # Month dropdown (1-12)
        month_combobox = ctk.CTkComboBox(dob_frame, values=[str(i).zfill(2) for i in range(1, 13)], width=80)
        month_combobox.pack(side="left", padx=5)

        # Year dropdown (1950 to current year)
        current_year = datetime.now().year
        year_combobox = ctk.CTkComboBox(dob_frame, values=[str(i) for i in range(1950, current_year + 1)], width=100)
        year_combobox.pack(side="left", padx=5)

        ctk.CTkLabel(scrollable_frame, text="Email (@gmail.com):").pack(pady=5)
        email_entry = ctk.CTkEntry(scrollable_frame, width=200)
        email_entry.pack(pady=5)

        ctk.CTkLabel(scrollable_frame, text="Phone (10 digits):").pack(pady=5)
        phone_entry = ctk.CTkEntry(scrollable_frame, width=200)
        phone_entry.pack(pady=5)

        ctk.CTkLabel(scrollable_frame, text="GitHub Token:").pack(pady=5)
        github_token_entry = ctk.CTkEntry(scrollable_frame, width=200)
        github_token_entry.pack(pady=5)

        ctk.CTkLabel(scrollable_frame, text="Access Tokens:").pack(pady=5)
        access_tokens_entry = ctk.CTkEntry(scrollable_frame, width=200)
        access_tokens_entry.pack(pady=5)

        def perform_signup():
            new_username = new_username_entry.get()
            new_password = new_password_entry.get()
            full_name = full_name_entry.get()
            gender = gender_combobox.get()
            day = day_combobox.get()
            month = month_combobox.get()
            year = year_combobox.get()
            email = email_entry.get()
            phone = phone_entry.get()
            github_token = github_token_entry.get()
            access_tokens = access_tokens_entry.get()

            # Combine day, month, and year into a single date string
            dob = f"{day}-{month}-{year}"

            # Validate inputs
            if not validate_username(new_username):
                messagebox.showwarning("Error", "Username must be more than 4 characters (digits or alphabets).")
                return
            if not validate_password(new_password):
                messagebox.showwarning("Error", "Password must be exactly 4 digits.")
                return
            if not validate_email(email):
                messagebox.showwarning("Error", "Email must be a valid @gmail.com address.")
                return
            if not validate_phone(phone):
                messagebox.showwarning("Error", "Phone number must be exactly 10 digits.")
                return

            # Check if username already exists
            user_data = load_user_data()
            for user in user_data:
                if user["username"] == new_username:
                    messagebox.showwarning("Error", "Username already exists. Choose a different username.")
                    return

            # Save new user
            encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()
            user_data.append({
                "username": new_username,
                "password": encrypted_password,
                "full_name": full_name,
                "gender": gender,
                "dob": dob,
                "email": email,
                "phone": phone,
                "github_token": github_token,
                "access_tokens": access_tokens
            })
            save_user_data(user_data)
            messagebox.showinfo("Success", "Signup successful!")
            signup_window.destroy()
            root.deiconify()  # Reopen the login window

        ctk.CTkButton(scrollable_frame, text="Signup", command=perform_signup, fg_color="#008CBA").pack(pady=10)
        ctk.CTkButton(scrollable_frame, text="Back", command=lambda: [signup_window.destroy(), root.deiconify()], fg_color="#d9534f").pack(pady=5)

    def open_delete_window():
        root.withdraw()  # Hide the login window
        delete_window = ctk.CTkToplevel()
        delete_window.title("Delete Account")
        delete_window.geometry("600x500")  # Increased window size

        # Set icon for the child window
        if os.path.exists(ICON_PHOTO_PATH):
            icon_photo = ctk.CTkImage(light_image=ICON_PHOTO_PATH, dark_image=ICON_PHOTO_PATH, size=(32, 32))
            delete_window.iconphoto(False, icon_photo)

        frame = ctk.CTkFrame(delete_window)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Delete Account", font=("Arial", 16)).pack(pady=10)

        ctk.CTkLabel(frame, text="Username:").pack(pady=5)
        delete_username_entry = ctk.CTkEntry(frame, width=200)
        delete_username_entry.pack(pady=5)

        ctk.CTkLabel(frame, text="Password:").pack(pady=5)
        delete_password_entry = ctk.CTkEntry(frame, show="*", width=200)
        delete_password_entry.pack(pady=5)

        def perform_delete():
            username = delete_username_entry.get()
            password = delete_password_entry.get()

            user_data = load_user_data()
            for user in user_data:
                if user["username"] == username:
                    try:
                        decrypted_password = cipher_suite.decrypt(user["password"].encode()).decode()
                        if decrypted_password == password:
                            user_data.remove(user)
                            save_user_data(user_data)
                            messagebox.showinfo("Success", "Account deleted successfully!")
                            delete_window.destroy()
                            root.deiconify()  # Reopen the login window
                            return
                    except Exception:
                        messagebox.showerror("Error", "Data corrupted or invalid key.")
                        return
            messagebox.showwarning("Error", "Invalid credentials.")

        ctk.CTkButton(frame, text="Delete", command=perform_delete, fg_color="#d9534f").pack(pady=10)
        ctk.CTkButton(frame, text="Back", command=lambda: [delete_window.destroy(), root.deiconify()], fg_color="#008CBA").pack(pady=5)

    root = ctk.CTk()
    root.title("Marcus Assists - Secure Login")
    root.geometry("800x300")

    # Set icon for the main window
    if os.path.exists(ICON_PATH):
        root.iconbitmap(ICON_PATH)

    # Handle window close event
    def on_closing():
        sys.exit()  # Exit the program when the window is closed

    root.protocol("WM_DELETE_WINDOW", on_closing)

    frame = ctk.CTkFrame(root)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="Username:").pack(pady=5)
    username_entry = ctk.CTkEntry(frame, width=200)
    username_entry.pack(pady=5)

    ctk.CTkLabel(frame, text="Password:").pack(pady=5)
    password_entry = ctk.CTkEntry(frame, show="*", width=200)
    password_entry.pack(pady=5)

    ctk.CTkButton(frame, text="Login", command=attempt_login, fg_color="#008CBA").pack(pady=5)

    # Buttons for Signup and Delete Account
    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(pady=10)

    ctk.CTkButton(button_frame, text="Signup", command=open_signup_window, fg_color="#008CBA").pack(side="left", padx=10)
    ctk.CTkButton(button_frame, text="Delete Account", command=open_delete_window, fg_color="#d9534f").pack(side="left", padx=10)

    success_label = ctk.CTkLabel(frame, text="", text_color="white")  # Status message
    success_label.pack(pady=5)

    root.mainloop()

    return success  # Return login success status

