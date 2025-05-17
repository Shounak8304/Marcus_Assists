import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os

def start_money_manager(money_management_active, money_management_window, money_management_close_event):
    """Starts the money manager GUI in a separate thread with provided global variables."""
    # Function to generate dates for a given month and year
    def generate_dates(month, year):
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        dates = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
        return dates

    # Function for two-finger scrolling
    def on_touchpad_scroll(event):
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")

    # Function to update the dates displayed based on the selected month
    def update_dates(event=None):
        selected_month = month_combobox.current() + 1
        selected_year = datetime.today().year

        nonlocal dates, note_entries, spent_entries, data_store
        dates = generate_dates(selected_month, selected_year)

        note_entries.clear()
        spent_entries.clear()

        for widget in content_frame.winfo_children():
            widget.grid_forget()

        header = ['Date', 'Note', 'Money Spent']
        for col, text in enumerate(header):
            if text == 'Date':
                month_combobox.grid(row=0, column=col, padx=3, pady=3)
            else:
                label = tk.Label(content_frame, text=text, width=15, relief="flat", anchor="center",
                               bg="#2b2b2b", fg="white", borderwidth=0)
                label.grid(row=0, column=col, padx=3, pady=3)

        for i, date in enumerate(dates):
            date_label = tk.Label(content_frame, text=date.strftime('%Y-%m-%d'), width=15, relief="flat",
                                anchor="center", bg="#2b2b2b", fg="white", borderwidth=0)
            date_label.grid(row=i+1, column=0, padx=3, pady=3)

            note_entry = tk.Entry(content_frame, width=15, bg="#404040", fg="white",
                                insertbackground="white", borderwidth=1, relief="solid")
            note_entry.grid(row=i+1, column=1, padx=3, pady=3)
            note_entries.append(note_entry)

            spent_entry = tk.Entry(content_frame, width=15, validate="key", validatecommand=vcmd,
                                 bg="#404040", fg="white", insertbackground="white", borderwidth=1, relief="solid")
            spent_entry.grid(row=i+1, column=2, padx=3, pady=3)
            spent_entries.append(spent_entry)

            key = date.strftime('%Y-%m-%d')
            if key in data_store:
                note_entry.insert(0, data_store[key]['note'])
                spent_entry.insert(0, data_store[key]['spent'])

        total_label = tk.Label(content_frame, text="Total", width=15, relief="flat", anchor="center",
                             bg="#2b2b2b", fg="white", borderwidth=0)
        total_label.grid(row=len(dates)+1, column=0, padx=3, pady=3)

        nonlocal total_spent_label
        total_spent_label = tk.Label(content_frame, text="0.0", width=15, relief="flat", anchor="center",
                                   bg="#2b2b2b", fg="white", borderwidth=0)
        total_spent_label.grid(row=len(dates)+1, column=2, padx=3, pady=3)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"), bg="#2b2b2b")
        update_total()

    # Function to save entered data and update total
    def save_data():
        total_spent = 0.0

        nonlocal dates, note_entries, spent_entries, data_store
        for i, date in enumerate(dates):
            note = note_entries[i].get()
            spent = spent_entries[i].get()

            try:
                spent_amount = float(spent) if spent else 0.0
                total_spent += spent_amount
            except ValueError:
                spent_amount = 0.0

            key = date.strftime('%Y-%m-%d')
            data_store[key] = {'note': note, 'spent': spent_amount}

        save_to_file()
        total_spent_label.config(text=f"{total_spent:.2f}")

    # Function to update total without saving
    def update_total():
        total_spent = 0.0
        nonlocal spent_entries
        for i in range(len(spent_entries)):
            spent = spent_entries[i].get()
            try:
                spent_amount = float(spent) if spent else 0.0
                total_spent += spent_amount
            except ValueError:
                continue
        total_spent_label.config(text=f"{total_spent:.2f}")

    # Function to save data_store to a file
    def save_to_file():
        nonlocal data_store
        with open("money_management.json", "w") as f:
            json.dump(data_store, f, indent=4)

    # Function to load data from file
    def load_from_file():
        nonlocal data_store
        if os.path.exists("money_management.json"):
            with open("money_management.json", "r") as f:
                data_store = json.load(f)
        else:
            data_store = {}

    # Function to remove data older than 1 year
    def remove_old_data():
        current_date = datetime.today()
        cutoff_date = current_date - timedelta(days=365)

        nonlocal data_store
        keys_to_remove = []
        for key in data_store:
            key_date = datetime.strptime(key, '%Y-%m-%d')
            if key_date < cutoff_date:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del data_store[key]

        save_to_file()

    # Validation function for numeric input
    def validate_numeric_input(P):
        if P == "" or P.replace('.', '', 1).isdigit():
            return True
        return False

    # GUI Setup
    root = tk.Tk()
    root.title("Money Manager")
    root.geometry("850x850")
    root.configure(bg="#1a1a1a")

    # Set window icon if available
    icon_path = "circle_logo.png"
    if os.path.exists(icon_path):
        icon_image = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_image)

    # Create scrollable frame
    frame = tk.Frame(root, bg="#252525")
    frame.pack(pady=10, padx=10, fill="both", expand=True)
    canvas = tk.Canvas(frame, bg="#2b2b2b", highlightthickness=0)
    scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview, bg="#252525", 
                           troughcolor="#1a1a1a", highlightthickness=0, bd=0)
    canvas.configure(yscrollcommand=scroll_y.set)
    content_frame = tk.Frame(canvas, bg="#2b2b2b")
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    scroll_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Bind touchpad scrolling (two-finger scroll)
    canvas.bind_all("<Button-4>", on_touchpad_scroll)
    canvas.bind_all("<Button-5>", on_touchpad_scroll)
    canvas.bind_all("<MouseWheel>", on_touchpad_scroll)

    # Validation command for numeric input
    vcmd = (root.register(validate_numeric_input), '%P')

    # Month selection
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    month_combobox = ttk.Combobox(content_frame, values=months, width=15, state="readonly")
    month_combobox.set(months[datetime.today().month - 1])
    month_combobox.bind("<<ComboboxSelected>>", update_dates)

    # Style for combobox to match dark theme
    style = ttk.Style(root)
    style.theme_use('default')
    style.configure("TCombobox", fieldbackground="#404040", background="#252525",
                    foreground="white", bordercolor="#252525", arrowcolor="white")
    style.map("TCombobox", fieldbackground=[("readonly", "#404040")])

    # Initialize variables within the function scope
    dates = generate_dates(datetime.today().month, datetime.today().year)
    note_entries, spent_entries, data_store = [], [], {}
    total_spent_label = None

    # Load existing data and initialize GUI
    load_from_file()
    remove_old_data()
    update_dates()

    # Save button
    save_button = tk.Button(root, text="Save Data", command=save_data, bg="#005ea6", fg="white",
                           activebackground="#004080", activeforeground="white", borderwidth=1, relief="flat")
    save_button.pack(pady=5)

    # Bind entry changes to update total
    root.after(100, lambda: [entry.bind('<KeyRelease>', lambda e: update_total()) 
                            for entry in spent_entries])

    money_management_window[0] = root  # Update the list reference
    money_management_active[0] = True  # Update the list reference
    money_management_close_event.clear()  # Reset the close event

    def check_close():
        if money_management_close_event.is_set() and money_management_window[0].winfo_exists():
            money_management_window[0].quit()
            money_management_window[0].destroy()
        if money_management_active[0]:
            root.after(100, check_close)  # Check every 100ms

    root.after(100, check_close)  # Start checking for close event

    try:
        root.mainloop()  # Run the Tkinter event loop in this thread
    finally:
        print("🛑 Money manager GUI closed.")
        money_management_active[0] = False  # Update the list reference
        money_management_window[0] = None  # Update the list reference
        money_management_close_event.clear()