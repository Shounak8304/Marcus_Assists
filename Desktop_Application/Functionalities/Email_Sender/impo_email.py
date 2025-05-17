import smtplib
import json
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from email.message import EmailMessage

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")  # Options: "Light", "Dark", "System"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Function to send email
def send_email(sender_email, sender_password, recipient_email, subject, content, attachment_path=None):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(content)

    if attachment_path:
        try:
            with open(attachment_path, 'rb') as attachment:
                msg.add_attachment(attachment.read(), maintype='application', subtype='octet-stream', filename=os.path.basename(attachment_path))
        except FileNotFoundError:
            messagebox.showerror("Error", "Attachment not found. Email will be sent without attachment.")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        messagebox.showinfo("Success", "Email Sent Successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {str(e)}")

# File for storing recipient emails
recipient_file = "recipients.json"

# Load or initialize recipient mapping with error handling
if os.path.exists(recipient_file) and os.path.getsize(recipient_file) > 0:
    try:
        with open(recipient_file, "r") as file:
            recipient_mapping = json.load(file)
    except json.JSONDecodeError:
        recipient_mapping = {}
        with open(recipient_file, "w") as file:
            json.dump(recipient_mapping, file, indent=4)
else:
    recipient_mapping = {}

# Email credentials
sender_email = "arankallesahil@gmail.com"
sender_password = "lsel orww ahof wkex"  # Use an App Password for security

# GUI Application
class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Sender")
        self.root.geometry("450x600")

        # Welcome Label
        self.welcome_label = ctk.CTkLabel(master=root, text="Hello, I am your email assistant", font=("Arial", 16, "bold"))
        self.welcome_label.pack(pady=20)

        # Recipient Name
        self.recipient_label = ctk.CTkLabel(master=root, text="Recipient's Name:")
        self.recipient_label.pack()
        self.recipient_name = ctk.CTkEntry(master=root, width=300)
        self.recipient_name.pack(pady=5)

        # Subject
        self.subject_label = ctk.CTkLabel(master=root, text="Subject:")
        self.subject_label.pack()
        self.subject = ctk.CTkEntry(master=root, width=300)
        self.subject.pack(pady=5)

        # Content
        self.content_label = ctk.CTkLabel(master=root, text="Email Content:")
        self.content_label.pack()
        self.content = ctk.CTkTextbox(master=root, height=150, width=300)
        self.content.pack(pady=10)

        # Attachment Section
        self.attach_var = ctk.BooleanVar()
        self.attach_checkbox = ctk.CTkCheckBox(master=root, text="Attach a file?", variable=self.attach_var, command=self.toggle_attach)
        self.attach_checkbox.pack(pady=5)
        self.attach_button = ctk.CTkButton(master=root, text="Select File", command=self.select_file, state="disabled")
        self.attach_button.pack(pady=5)
        self.attachment_path = None

        # Send Button
        self.send_button = ctk.CTkButton(master=root, text="Send Email", command=self.send_email_gui)
        self.send_button.pack(pady=20)

    def toggle_attach(self):
        self.attach_button.configure(state="normal" if self.attach_var.get() else "disabled")

    def select_file(self):
        self.attachment_path = filedialog.askopenfilename(title="Select a file to attach")
        if not self.attachment_path:
            messagebox.showinfo("Info", "No file selected. Email will be sent without attachment.")

    def send_email_gui(self):
        recipient_name = self.recipient_name.get().lower().strip()
        if not recipient_name:
            messagebox.showerror("Error", "Please enter a recipient name")
            return

        recipient_email = recipient_mapping.get(recipient_name)
        if not recipient_email:
            recipient_email = self.ask_recipient_email(recipient_name)
            if not recipient_email:
                return

        subject = self.subject.get().strip()
        if not subject:
            messagebox.showerror("Error", "Please enter a subject")
            return

        content = self.content.get("0.0", "end").strip()
        if not content:
            messagebox.showerror("Error", "Please enter email content")
            return

        attachment_path = self.attachment_path if self.attach_var.get() else None

        send_email(sender_email, sender_password, recipient_email, subject, content, attachment_path)
        self.root.destroy()  # Exit the application after sending the email

    def ask_recipient_email(self, recipient_name):
        email_window = ctk.CTkToplevel(self.root)
        email_window.title("New Recipient")
        email_window.geometry("350x200")
        email_window.grab_set()  # Make it modal

        ctk.CTkLabel(master=email_window, text=f"Recipient '{recipient_name}' not found.").pack(pady=10)
        ctk.CTkLabel(master=email_window, text="Please enter their email:").pack(pady=5)
        
        email_entry = ctk.CTkEntry(master=email_window, width=250)
        email_entry.pack(pady=10)

        recipient_email = [None]
        
        def save_email():
            email = email_entry.get().strip()
            if email:
                recipient_mapping[recipient_name] = email
                with open(recipient_file, "w") as file:
                    json.dump(recipient_mapping, file, indent=4)  # Save properly formatted JSON
                messagebox.showinfo("Success", "Recipient saved successfully!")
                recipient_email[0] = email
            email_window.destroy()

        save_button = ctk.CTkButton(master=email_window, text="Save", command=save_email)
        save_button.pack(pady=10)

        email_window.wait_window()
        return recipient_email[0]

# Function to run the application
def run_email_app():
    root = ctk.CTk()
    app = EmailApp(root)
    root.mainloop()
    
