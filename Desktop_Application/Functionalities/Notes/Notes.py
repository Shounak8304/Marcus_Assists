import os
import time
import pyautogui
import customtkinter as ctk

def sticky_notes_gui():
    def handle_done(event=None):
        content = text_widget.get("1.0", "end").strip()
        if content.endswith("DONE"):
            note_text = content[:-4].strip()
            try:
                os.system("start explorer.exe shell:appsFolder\\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe!App")
                time.sleep(5)
                pyautogui.hotkey("ctrl", "n")
                time.sleep(1)
                pyautogui.write(note_text, interval=0.05)
                time.sleep(2)
                os.system("taskkill /IM Microsoft.Notes.exe /F")
                result_label.configure(text="Sticky note created and closed successfully!", text_color="green")
                root.after(2000, root.destroy)
            except Exception as e:
                result_label.configure(text=f"An error occurred: {e}", text_color="red")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Sticky Notes Terminal")
    root.geometry("800x600")

    font = ("Courier", 14)
    text_widget = ctk.CTkTextbox(root, fg_color="black", text_color="white", font=font, wrap="word")
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)
    text_widget.focus()

    result_label = ctk.CTkLabel(root, text="", text_color="green", font=font)
    result_label.pack(pady=5)

    text_widget.bind("<Return>", handle_done)
    root.mainloop()


