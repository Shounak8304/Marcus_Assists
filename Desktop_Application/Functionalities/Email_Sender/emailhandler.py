import imaplib
import email
import smtplib
import os
import subprocess
import threading
from email import policy
from email.parser import BytesParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import scrolledtext, Entry, Label
from cryptography.fernet import Fernet

# Files for credentials and encryption key
CREDENTIALS_FILE = "email_credentials.txt"
KEY_FILE = "email_key.key"

# Email-related functions (unchanged)
def get_downloads_folder():
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:  # macOS and Linux
        return os.path.join(os.path.expanduser('~'), 'Downloads')

def open_attachment(file_path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.uname().sysname == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        print(f"Opened: {file_path}")
    except Exception as e:
        print(f"Error opening file: {e}")

def download_attachments(email_message):
    downloads_folder = get_downloads_folder()
    attachment_files = []
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if filename:
            filepath = os.path.join(downloads_folder, filename)
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join(downloads_folder, f"{name}_{counter}{ext}")
                counter += 1
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            attachment_files.append(filepath)
            print(f"Downloaded: {os.path.basename(filepath)}")
    return attachment_files

def send_reply(sender_email, sender_password, receiver_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Reply sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending reply: {e}")
        return False

def forward_email(sender_email, sender_password, receiver_email, original_sender, original_subject, original_body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"Fwd: {original_subject}"
    forwarded_content = f"""
---------- Forwarded message ----------
From: {original_sender}
Subject: {original_subject}

{original_body}
"""
    msg.attach(MIMEText(forwarded_content, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email forwarded successfully!")
        return True
    except Exception as e:
        print(f"Error forwarding email: {e}")
        return False

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

def encrypt_credentials(email_address, password, key):
    fernet = Fernet(key)
    credentials = f"{email_address}\n{password}".encode()
    encrypted = fernet.encrypt(credentials)
    with open(CREDENTIALS_FILE, 'wb') as f:
        f.write(encrypted)
    print(f"Encrypted credentials saved to {CREDENTIALS_FILE}")

def decrypt_credentials(key):
    if os.path.exists(CREDENTIALS_FILE):
        try:
            fernet = Fernet(key)
            with open(CREDENTIALS_FILE, 'rb') as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted).decode()
            lines = decrypted.split('\n')
            if len(lines) == 2:
                return lines[0], lines[1]
        except Exception as e:
            print(f"Error decrypting credentials: {e}")
    return None, None

# GUI Class
class EmailClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Client")

        # Dark theme colors (aligned with FileNavigatorApp)
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#2e2e2e"
        self.button_bg = "#3e3e3e"
        self.button_fg = "#ffffff"
        self.highlight_color = "#4e4e4e"
        self.root.configure(bg=self.bg_color)

        # Window size and position (aligned with FileNavigatorApp)
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        position_right = screen_width - window_width
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+0')

        # Email state
        self.email_address = None
        self.password = None
        self.mail = None
        self.email_list = []
        self.is_fetching = False
        self.encryption_key = generate_key()
        self.current_state = None
        self.current_email = None
        self.options_window = None

        # GUI setup
        self.status_label = Label(
            root, text="Email Client Started", anchor="w", fg=self.fg_color, 
            bg=self.bg_color, font=("Arial", 12)
        )
        self.status_label.pack(fill="x", padx=10, pady=10)

        self.display_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, height=30, bg=self.entry_bg, fg=self.fg_color, 
            font=("Consolas", 12), insertbackground=self.fg_color
        )
        self.display_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.display_area.insert(tk.END, "Welcome to Email Client! Use commands like 'retrieve <number>' or 'unseen'.\n")
        self.display_area.config(state=tk.DISABLED)

        self.command_entry = Entry(
            root, bg=self.entry_bg, fg=self.fg_color, font=("Arial", 12), 
            insertbackground=self.fg_color
        )
        self.command_entry.pack(fill="x", padx=10, pady=10)
        self.command_entry.bind("<Return>", self.execute_command)

        # Load credentials and connect
        self.load_and_connect()

    def load_and_connect(self):
        self.email_address, self.password = decrypt_credentials(self.encryption_key)
        if self.email_address and self.password:
            self.display_message(f"Loaded email: {self.email_address}")
            self.connect_to_server()
        else:
            self.display_message("No saved credentials found. Type 'set email <your_email>' to set email address.")

    def connect_to_server(self):
        try:
            if not self.email_address or not self.password:
                self.display_message("Please set email and password first.")
                return
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(self.email_address, self.password)
            self.mail.select('inbox')
            self.display_message("Connected to email server!")
            encrypt_credentials(self.email_address, self.password, self.encryption_key)
            self.show_unseen_count()
        except Exception as e:
            self.display_message(f"Connection failed: {e}")
            self.mail = None
            self.display_message("Please set new credentials with 'set email <your_email>' and 'set password <your_password>'.")

    def show_unseen_count(self):
        threading.Thread(target=self._show_unseen_count_thread, daemon=True).start()

    def _show_unseen_count_thread(self):
        try:
            if not self.mail:
                self.display_message("Not connected to server.")
                return
            status, response = self.mail.status('inbox', '(UNSEEN)')
            if status == 'OK':
                unseen_count = int(response[0].decode().split()[2].strip(').,]'))
                self.display_message(f"Number of unseen emails: {unseen_count}")
                self.display_message("Type 'retrieve <number>' or 'retrieve all' to fetch emails, 'unseen' for unseen emails.")
            else:
                self.display_message("Error fetching unseen email count.")
        except Exception as e:
            self.display_message(f"Error: {e}")

    def fetch_emails(self, num_emails):
        if not self.mail:
            self.display_message("Not connected to server.")
            return
        if self.is_fetching:
            self.display_message("Fetching in progress, please wait.")
            return
        self.is_fetching = True
        threading.Thread(target=self._fetch_emails_thread, args=(num_emails,), daemon=True).start()

    def _fetch_emails_thread(self, num_emails):
        try:
            status, messages = self.mail.search(None, 'ALL')
            if status != 'OK':
                self.display_message("Error fetching emails.")
                self.is_fetching = False
                return

            email_ids = messages[0].split()
            if not email_ids:
                self.display_message("No emails found!")
                self.is_fetching = False
                return

            if num_emails.lower() == "all":
                num_to_fetch = len(email_ids)
            else:
                num_to_fetch = min(int(num_emails), len(email_ids))

            email_ids_to_fetch = email_ids[-num_to_fetch:]

            self.email_list = []
            self.display_area.config(state=tk.NORMAL)
            self.display_area.delete(1.0, tk.END)
            self.display_area.insert(tk.END, "Recent Emails:\n\n")

            for index, email_id in enumerate(reversed(email_ids_to_fetch), start=1):
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                        sender = msg['from']
                        subject = msg['subject']
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            if msg.get_content_type() == "text/plain":
                                body = msg.get_payload(decode=True).decode(errors='ignore')

                        self.email_list.append({
                            'index': index,
                            'sender': sender,
                            'subject': subject,
                            'body': body,
                            'attachments': [],
                            'email_id': email_id,
                            'message': msg
                        })

                        self.display_area.insert(tk.END, f"{index}. From: {sender}\n")
                        self.display_area.insert(tk.END, f"   Subject: {subject}\n")
                        self.display_area.insert(tk.END, f"   Body: {body}\n")
                        self.display_area.insert(tk.END, "   Attachments: Not downloaded yet\n")
                        self.display_area.insert(tk.END, "-" * 50 + "\n")

            self.display_area.config(state=tk.DISABLED)
            self.display_message("Type 'select <number>' to view an email, 'unseen' for unseen emails.")
            self.is_fetching = False
        except Exception as e:
            self.display_message(f"Error fetching emails: {e}")
            self.is_fetching = False

    def fetch_unseen_emails(self):
        if not self.mail:
            self.display_message("Not connected to server.")
            return
        if self.is_fetching:
            self.display_message("Fetching in progress, please wait.")
            return
        self.is_fetching = True
        threading.Thread(target=self._fetch_unseen_emails_thread, daemon=True).start()

    def _fetch_unseen_emails_thread(self):
        try:
            status, messages = self.mail.search(None, 'UNSEEN')
            if status != 'OK':
                self.display_message("Error fetching unseen emails.")
                self.is_fetching = False
                return

            email_ids = messages[0].split()
            if not email_ids:
                self.display_message("No unseen emails found!")
                self.is_fetching = False
                return

            self.email_list = []
            self.display_area.config(state=tk.NORMAL)
            self.display_area.delete(1.0, tk.END)
            self.display_area.insert(tk.END, "Unseen Emails:\n\n")

            for index, email_id in enumerate(reversed(email_ids), start=1):
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                        sender = msg['from']
                        subject = msg['subject']
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            if msg.get_content_type() == "text/plain":
                                body = msg.get_payload(decode=True).decode(errors='ignore')

                        self.email_list.append({
                            'index': index,
                            'sender': sender,
                            'subject': subject,
                            'body': body,
                            'attachments': [],
                            'email_id': email_id,
                            'message': msg
                        })

                        self.display_area.insert(tk.END, f"{index}. From: {sender}\n")
                        self.display_area.insert(tk.END, f"   Subject: {subject}\n")
                        self.display_area.insert(tk.END, f"   Body: {body}\n")
                        self.display_area.insert(tk.END, "   Attachments: Not downloaded yet\n")
                        self.display_area.insert(tk.END, "-" * 50 + "\n")

            self.display_area.config(state=tk.DISABLED)
            self.display_message("Type 'select <number>' to view an email.")
            self.is_fetching = False
        except Exception as e:
            self.display_message(f"Error fetching unseen emails: {e}")
            self.is_fetching = False

    def execute_command(self, event=None):
        command = self.command_entry.get().strip()
        self.command_entry.delete(0, tk.END)
        self.handle_command(command)

    def handle_command(self, command):
        """Handle commands from server or GUI."""
        if self.is_fetching:
            self.display_message("Operation in progress, please wait.")
            return

        self.display_message(f"Received command: {command}")

        # Note: No explicit "close" command handling here; closure is managed in main.py

        # Handle state-based inputs
        if self.current_state == "reply_body" and self.current_email:
            threading.Thread(target=self._send_reply_thread,
                            args=(self.current_email['sender'], f"Re: {self.current_email['subject']}", command, self.options_window),
                            daemon=True).start()
            self.current_state = None
            self.current_email = None
            return

        elif self.current_state == "forward_address" and self.current_email:
            threading.Thread(target=self._forward_email_thread,
                            args=(command, self.current_email['sender'], self.current_email['subject'], self.current_email['body'], self.options_window),
                            daemon=True).start()
            self.current_state = None
            self.current_email = None
            return

        # Handle email-specific commands when an email is selected
        if self.current_email:
            if command.lower() == "reply":
                self.current_state = "reply_body"
                self.display_message("Please type your reply message and press Enter.")
                return

            elif command.lower() == "forward":
                self.current_state = "forward_address"
                self.display_message("Please type the forward email address and press Enter.")
                return

            elif command.lower() == "attachments":
                if not self.current_email.get('message'):
                    self.display_message("No email message available to check attachments!")
                else:
                    attachments = download_attachments(self.current_email['message'])
                    self.current_email['attachments'] = attachments
                    if attachments:
                        self.display_message("Attachments downloaded:")
                        for i, path in enumerate(attachments, 1):
                            self.display_message(f"{i}. {os.path.basename(path)}")
                        self.display_message("Type 'download' to re-download or 'open <number>' to open an attachment.")
                    else:
                        self.display_message("No attachments found in this email.")
                return

            elif command.lower() == "download" and self.current_email.get('message'):
                new_attachments = download_attachments(self.current_email['message'])
                if new_attachments:
                    self.current_email['attachments'] = new_attachments
                    self.display_message(f"Re-downloaded attachments: {', '.join([os.path.basename(a) for a in new_attachments])}")
                else:
                    self.display_message("No new attachments downloaded.")
                return

            elif command.lower().startswith("open ") and self.current_email['attachments']:
                try:
                    attachment_num = int(command[5:].strip()) - 1
                    if 0 <= attachment_num < len(self.current_email['attachments']):
                        open_attachment(self.current_email['attachments'][attachment_num])
                        self.display_message(f"Opened attachment: {os.path.basename(self.current_email['attachments'][attachment_num])}")
                    else:
                        self.display_message(f"Invalid attachment number! Valid range: 1 to {len(self.current_email['attachments'])}")
                except ValueError:
                    self.display_message("Invalid format. Use: open <number> (e.g., open 1)")
                return

            elif command.lower() == "back":
                if self.options_window and self.options_window.winfo_exists():
                    self.options_window.destroy()
                self.current_state = None
                self.current_email = None
                self.display_message("Returned to email list. Type 'select <number>' to view another email.")
                return

            else:
                self.display_message("Unknown command. Use: 'reply', 'forward', 'attachments', 'download', 'open <number>', or 'back'")
                return

        # Regular commands
        if command.lower().startswith("set email "):
            self.email_address = command[10:].strip()
            self.display_message(f"Email set to: {self.email_address}")
            if self.password:
                self.connect_to_server()

        elif command.lower().startswith("set password "):
            self.password = command[13:].strip()
            self.display_message("Password set.")
            if self.email_address:
                self.connect_to_server()

        elif command.lower().startswith("select "):
            if not self.mail:
                self.display_message("Not connected to server.")
                return
            try:
                email_index = int(command[7:].strip()) - 1
                if 0 <= email_index < len(self.email_list):
                    self.show_email_options(self.email_list[email_index])
                else:
                    self.display_message(f"Invalid email number! Valid range: 1 to {len(self.email_list)}")
            except ValueError:
                self.display_message("Invalid format. Use: select <number>")

        elif command.lower() == "unseen":
            self.fetch_unseen_emails()

        elif command.lower().startswith("retrieve "):
            try:
                num_emails = command[9:].strip()
                if num_emails.lower() == "all" or int(num_emails) > 0:
                    self.fetch_emails(num_emails)
                else:
                    self.display_message("Please enter 'all' or a positive number of emails to retrieve.")
            except ValueError:
                self.display_message("Invalid format. Use: retrieve <number> or retrieve all (e.g., retrieve 3)")

        else:
            self.display_message(f"Unknown command: {command}")

    def show_email_options(self, email):
        self.current_email = email
        self.display_message(f"Selected email: {email['subject']}")
        self.options_window = tk.Toplevel(self.root)
        self.options_window.title(f"Email: {email['subject']}")
        self.options_window.configure(bg=self.bg_color)
        self.options_window.geometry("600x400")

        email_text = scrolledtext.ScrolledText(
            self.options_window, wrap=tk.WORD, height=15, bg=self.entry_bg, 
            fg=self.fg_color, font=("Consolas", 12)
        )
        email_text.pack(fill="both", expand=True, padx=10, pady=10)
        email_text.insert(tk.END, f"From: {email['sender']}\n")
        email_text.insert(tk.END, f"Subject: {email['subject']}\n")
        email_text.insert(tk.END, f"Body: {email['body']}\n")
        if email['attachments']:
            email_text.insert(tk.END, f"Attachments: {', '.join([os.path.basename(a) for a in email['attachments']])}\n")
        else:
            email_text.insert(tk.END, "Attachments: Not downloaded yet\n")
        email_text.config(state=tk.DISABLED)

        self.display_message("Email selected. Use commands: 'reply', 'forward', 'attachments', 'download', 'open <number>', 'back'")

    def _send_reply_thread(self, receiver_email, subject, body, window):
        self.is_fetching = True
        if send_reply(self.email_address, self.password, receiver_email, subject, body):
            self.display_message("Reply sent!")
            if window and window.winfo_exists():
                window.destroy()
        else:
            self.display_message("Failed to send reply.")
        self.is_fetching = False

    def _forward_email_thread(self, receiver_email, original_sender, original_subject, original_body, window):
        self.is_fetching = True
        if forward_email(self.email_address, self.password, receiver_email, original_sender, original_subject, original_body):
            self.display_message("Email forwarded!")
            if window and window.winfo_exists():
                window.destroy()
        else:
            self.display_message("Failed to forward email.")
        self.is_fetching = False

    def display_message(self, message):
        self.display_area.config(state=tk.NORMAL)
        self.display_area.insert(tk.END, f"{message}\n")
        self.display_area.yview(tk.END)
        self.display_area.config(state=tk.DISABLED)