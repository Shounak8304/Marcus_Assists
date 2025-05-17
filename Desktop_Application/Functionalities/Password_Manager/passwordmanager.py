import os
import json
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import threading
from tkinter.simpledialog import Dialog

def generate_key():
    """Generate and save a key for encryption."""
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Load the encryption key from file."""
    if not os.path.exists("key.key"):
        return generate_key()
    with open("key.key", "rb") as key_file:
        return key_file.read()

def encrypt_data(data, key):
    """Encrypt data using the provided key."""
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data, key):
    """Decrypt data using the provided key."""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()

def save_passwords(passwords):
    """Save passwords to a file."""
    with open("passwords.json", "w") as file:
        json.dump(passwords, file)

def load_passwords():
    """Load passwords from a file."""
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            return json.load(file)
    return {}

def add_password(service, username, password, key):
    """Add a new password to the password manager."""
    passwords = load_passwords()
    encrypted_password = encrypt_data(password, key)
    passwords[service] = {"username": username, "password": encrypted_password}
    save_passwords(passwords)

def delete_password(selection, key, table):
    """Delete a password entry."""
    if not selection:
        messagebox.showerror("Error", "No service selected.")
        return

    service = table.item(selection)['values'][0]
    passwords = load_passwords()

    if service in passwords:
        del passwords[service]
        save_passwords(passwords)
        update_table(key, table)
        messagebox.showinfo("Success", f"Password for {service} deleted.")
    else:
        messagebox.showerror("Error", f"No entry found for {service}.")

def edit_password(selection, key, table, parent):
    """Edit a password entry."""
    if not selection:
        messagebox.showerror("Error", "No service selected.")
        return

    service = table.item(selection)['values'][0]
    passwords = load_passwords()

    if service not in passwords:
        messagebox.showerror("Error", f"No entry found for {service}.")
        return

    service_entry = passwords[service]
    current_username = service_entry["username"]
    current_password = decrypt_data(service_entry["password"], key)

    top = tk.Toplevel(parent)
    top.title(f"Edit Password for {service}")
    top.configure(bg="black")

    tk.Label(top, text="Service Name:", bg="black", fg="white").grid(row=0, column=0, padx=5, pady=5)
    service_entry_widget = tk.Entry(top)
    service_entry_widget.insert(0, service)
    service_entry_widget.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(top, text="Username:", bg="black", fg="white").grid(row=1, column=0, padx=5, pady=5)
    username_entry = tk.Entry(top)
    username_entry.insert(0, current_username)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(top, text="Password:", bg="black", fg="white").grid(row=2, column=0, padx=5, pady=5)
    password_entry = tk.Entry(top, show="*")
    password_entry.insert(0, current_password)
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    def toggle_password_visibility():
        """Toggle visibility of the password."""
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    show_button = tk.Button(top, text="Show", command=toggle_password_visibility, bg="gray", fg="white")
    show_button.grid(row=3, column=0, columnspan=2, pady=10)

    def submit():
        new_service = service_entry_widget.get()
        new_username = username_entry.get()
        new_password = password_entry.get()
        if new_service and new_username and new_password:
            encrypted_password = encrypt_data(new_password, key)
            passwords[new_service] = {"username": new_username, "password": encrypted_password}
            if new_service != service:
                del passwords[service]
            save_passwords(passwords)
            update_table(key, table)
            messagebox.showinfo("Success", f"Password for {new_service} updated successfully.")
            top.destroy()
        else:
            messagebox.showerror("Error", "All fields are required!")

    submit_button = tk.Button(top, text="Submit", command=submit, bg="gray", fg="white")
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

def add_password_gui(key, table, parent):
    """GUI handler for adding a password."""
    top = tk.Toplevel(parent)
    top.title("Add Password")
    top.configure(bg="black")

    tk.Label(top, text="Service Name:", bg="black", fg="white").grid(row=0, column=0, padx=5, pady=5)
    service_entry = tk.Entry(top)
    service_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(top, text="Username:", bg="black", fg="white").grid(row=1, column=0, padx=5, pady=5)
    username_entry = tk.Entry(top)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(top, text="Password:", bg="black", fg="white").grid(row=2, column=0, padx=5, pady=5)
    password_entry = tk.Entry(top, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    def toggle_password_visibility():
        """Toggle visibility of the password."""
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
        else:
            password_entry.config(show="*")

    show_button = tk.Button(top, text="Show", command=toggle_password_visibility, bg="gray", fg="white")
    show_button.grid(row=3, column=0, columnspan=2, pady=10)

    def submit():
        service = service_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        if service and username and password:
            add_password(service, username, password, key)
            messagebox.showinfo("Success", f"Password for {service} added successfully.")
            update_table(key, table)
            top.destroy()
        else:
            messagebox.showerror("Error", "All fields are required!")

    submit_button = tk.Button(top, text="Submit", command=submit, bg="gray", fg="white")
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

def update_table(key, table):
    """Update the table with current passwords."""
    for row in table.get_children():
        table.delete(row)
    passwords = load_passwords()
    for service, credentials in passwords.items():
        username = credentials["username"]
        password = decrypt_data(credentials["password"], key)
        table.insert("", "end", values=(service, username, password))

def authenticate():
    """Prompt user for authentication password."""
    class AuthDialog(Dialog):
        def body(self, master):
            tk.Label(master, text="Enter Master Password:").grid(row=0, column=0)
            self.password_entry = tk.Entry(master, show="*")
            self.password_entry.grid(row=0, column=1)
            return self.password_entry

        def apply(self):
            self.result = self.password_entry.get()

    return AuthDialog(tk.Tk()).result

def create_master_password():
    """Create a master password for first-time users."""
    if os.path.exists("master_password.key"):
        return None  # Master password already exists

    top = tk.Toplevel()
    top.title("Create Master Password")
    top.configure(bg="black")

    tk.Label(top, text="Create a Master Password:", bg="black", fg="white").grid(row=0, column=0, padx=5, pady=5)
    password_entry = tk.Entry(top, show="*")
    password_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(top, text="Confirm Master Password:", bg="black", fg="white").grid(row=1, column=0, padx=5, pady=5)
    confirm_entry = tk.Entry(top, show="*")
    confirm_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        password = password_entry.get()
        confirm_password = confirm_entry.get()
        if password and confirm_password and password == confirm_password:
            with open("master_password.key", "w") as file:
                file.write(encrypt_data(password, load_key()))
            messagebox.showinfo("Success", "Master password created successfully.")
            top.destroy()
        else:
            messagebox.showerror("Error", "Passwords do not match or are empty.")

    submit_button = tk.Button(top, text="Submit", command=submit, bg="gray", fg="white")
    submit_button.grid(row=2, column=0, columnspan=2, pady=10)

    top.wait_window()  # Wait for the window to close

def load_master_password(key):
    """Load the master password from file."""
    if not os.path.exists("master_password.key"):
        return None
    with open("master_password.key", "r") as file:
        encrypted_password = file.read()
        return decrypt_data(encrypted_password, key)

def run_password_manager(password_manager_active, password_manager_window, close_event):
    """Run the password manager application."""
    key = load_key()

    # Check if master password exists
    if not os.path.exists("master_password.key"):
        create_master_password()

    master_password = load_master_password(key)
    if not master_password:
        messagebox.showerror("Error", "Failed to load master password. Exiting application.")
        return

    user_password = authenticate()
    if user_password != master_password:
        messagebox.showerror("Error", "Authentication failed. Exiting application.")
        return

    root = tk.Tk()
    root.title("Password Manager")
    root.configure(bg="black")

    frame = tk.Frame(root, bg="black")
    frame.pack(pady=10, padx=10)

    table = ttk.Treeview(frame, columns=("Service", "Username", "Password"), show="headings")
    table.heading("Service", text="Service")
    table.heading("Username", text="Username")
    table.heading("Password", text="Password")
    table.pack()

    style = ttk.Style()
    style.configure("Treeview", background="black", foreground="white", fieldbackground="black")
    style.configure("Treeview.Heading", background="gray", foreground="white")

    update_table(key, table)

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack(pady=10)

    add_button = tk.Button(button_frame, text="Add Password", command=lambda: add_password_gui(key, table, root), bg="gray", fg="white")
    add_button.grid(row=0, column=0, padx=5)

    delete_button = tk.Button(button_frame, text="Delete Password", command=lambda: delete_password(table.selection(), key, table), bg="gray", fg="white")
    delete_button.grid(row=0, column=1, padx=5)

    edit_button = tk.Button(button_frame, text="Edit Password", command=lambda: edit_password(table.selection(), key, table, root), bg="gray", fg="white")
    edit_button.grid(row=0, column=2, padx=5)

    exit_button = tk.Button(button_frame, text="Exit", command=root.destroy, bg="gray", fg="white")
    exit_button.grid(row=0, column=3, padx=5)

    # Update the active flag and window reference
    password_manager_active[0] = True
    password_manager_window[0] = root

    def check_close_event():
        """Check if the close event is set and close the window if it is."""
        if close_event.is_set():
            print("🛑 Closing password manager...")
            root.destroy()  # Forcefully close the Tkinter window
        else:
            # Check again after 100ms
            root.after(100, check_close_event)

    # Start checking for the close event
    root.after(100, check_close_event)

    # Start the Tkinter main loop
    root.mainloop()

    # Cleanup after the window is closed
    password_manager_active[0] = False
    password_manager_window[0] = None
    close_event.clear()
    print("🛑 Password manager closed.")
