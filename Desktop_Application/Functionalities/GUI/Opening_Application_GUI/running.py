import tkinter as tk

def fade_out(root, label, opacity):
    if opacity > 0:
        opacity -= 0.05  # Reduce opacity
        root.attributes('-alpha', opacity)  # Apply transparency
        root.after(150, fade_out, root, label, opacity)  # Repeat every 150ms
    else:
        root.destroy()  # Close the window

def show_floating_message():
    root = tk.Tk()
    root.configure(bg="black")
    root.attributes('-fullscreen', True)  # Fullscreen mode
    root.attributes('-topmost', True)  # Keep on top
    root.attributes('-alpha', 1.0)  # Fully visible

    label = tk.Label(root, text="Hello, World!", fg="white", bg="black", font=("Arial", 24))
    label.place(relx=0.5, rely=0.5, anchor="center")

    root.after(1000, fade_out, root, label, 1.0)  # Start fading after 1 second
    root.mainloop()

show_floating_message()
