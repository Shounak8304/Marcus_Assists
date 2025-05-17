import customtkinter as ctk
from github import Github
from tkinter import messagebox

# Replace 'your_personal_access_token' with your actual token
g = Github("")

def create_repository_ui():
    """Open the UI for creating a new repository."""
    def create_repository():
        """Create a new repository."""
        try:
            repo_name = repo_name_entry.get().strip()
            if not repo_name:
                messagebox.showwarning("Input Error", "Repository name cannot be empty!")
                return

            is_private = private_var.get() == 1  # 1 if checked, 0 if unchecked
            user = g.get_user()
            repo = user.create_repo(
                name=repo_name,
                description="Repository created using PyGithub",
                private=is_private,
                has_issues=True,
                has_wiki=True,
                has_projects=True,
            )
            messagebox.showinfo("Success", f"Repository '{repo_name}' created successfully!\nURL: {repo.html_url}")
            repo_name_entry.delete(0, ctk.END)  # Clear the entry field
            private_var.set(0)  # Uncheck the private checkbox
        except Exception as e:
            messagebox.showerror("Error", f"Error creating repository: {e}")

    # Create the creation window
    create_window = ctk.CTk()
    create_window.title("Create Repository")
    create_window.geometry("400x300")

    # Frame for creating a new repository
    create_frame = ctk.CTkFrame(create_window)
    create_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Label for creating a new repository
    create_label = ctk.CTkLabel(create_frame, text="Create New Repository:", font=("Arial", 14))
    create_label.pack(pady=10)

    # Entry for repository name
    repo_name_entry = ctk.CTkEntry(create_frame, width=300, placeholder_text="Enter repository name")
    repo_name_entry.pack(pady=10)

    # Checkbox for private repository
    private_var = ctk.IntVar()
    private_checkbox = ctk.CTkCheckBox(create_frame, text="Private Repository", variable=private_var)
    private_checkbox.pack(pady=10)

    # Button to create a new repository
    create_button = ctk.CTkButton(create_frame, text="Create Repository", command=create_repository)
    create_button.pack(pady=10)

    # Run the application
    create_window.mainloop()

# Run the creation UI directly
if __name__ == "__main__":
    create_repository_ui()