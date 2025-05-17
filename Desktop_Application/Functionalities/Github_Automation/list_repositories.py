import customtkinter as ctk
from github import Github
from tkinter import messagebox

# Replace 'your_personal_access_token' with your actual token
g = Github("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")

def list_repositories_ui():
    """Open the UI for listing repositories."""
    def refresh_repositories():
        """Refresh the repository list."""
        try:
            user = g.get_user()
            repos = list(user.get_repos())
            repo_textbox.delete("1.0", ctk.END)  # Clear the textbox
            for repo in repos:
                repo_textbox.insert(ctk.END, f"{repo.name} (Private: {repo.private})\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error listing repositories: {e}")

    # Create the listing window
    list_window = ctk.CTk()
    list_window.title("List Repositories")
    list_window.geometry("700x500")

    # Frame for the repository list
    repo_frame = ctk.CTkFrame(list_window)
    repo_frame.pack(pady=30, padx=30, fill="both", expand=True)

    # Label for the repository list
    repo_label = ctk.CTkLabel(repo_frame, text="Your Repositories:", font=("Arial", 14))
    repo_label.pack(pady=10)

    # Textbox to display repositories
    repo_textbox = ctk.CTkTextbox(repo_frame, width=500, height=300)
    repo_textbox.pack(pady=10)

    # Button to refresh the repository list
    refresh_button = ctk.CTkButton(repo_frame, text="Refresh List", command=refresh_repositories)
    refresh_button.pack(pady=10)

    # Automatically refresh the repository list when the window opens
    refresh_repositories()

    # Run the application
    list_window.mainloop()

# Run the listing UI directly
if __name__ == "__main__":
    list_repositories_ui()