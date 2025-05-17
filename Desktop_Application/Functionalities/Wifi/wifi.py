import subprocess
import customtkinter as ctk
from tkinter import messagebox

# Set CustomTkinter appearance mode and color theme
ctk.set_appearance_mode("System")  # Can be "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Can be "blue", "green", "dark-blue", etc.

def get_wifi_status():
    """Fetches and returns the current WiFi connection status."""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True, check=True)
        output = result.stdout.split('\n')
        wifi_info = {}
        for line in output:
            line = line.strip()
            if "State" in line:
                wifi_info["Status"] = line.split(":")[1].strip()
            elif "SSID" in line and "BSSID" not in line:
                wifi_info["SSID"] = line.split(":")[1].strip()
            elif "Signal" in line:
                wifi_info["Signal Strength"] = line.split(":")[1].strip()
        return wifi_info
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error retrieving WiFi status: {e}")
        return {}

def scan_wifi():
    """Scans and returns available WiFi networks."""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], capture_output=True, text=True, check=True)
        output = result.stdout.split('\n')
        networks = []
        for line in output:
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                networks.append(ssid)
        return networks
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error occurred while scanning WiFi networks: {e}")
        return []

def is_profile_saved(ssid):
    """Checks if a WiFi profile for the given SSID is already saved."""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], capture_output=True, text=True, check=True)
        return ssid in result.stdout
    except subprocess.CalledProcessError:
        return False

def connect_to_wifi(ssid, password=None, root=None):
    """Connects to the specified WiFi network and closes the window on success."""
    try:
        if is_profile_saved(ssid):
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True)
            messagebox.showinfo("Success", f"Connected to {ssid} successfully!")
            if root:
                root.destroy()  # Close the WiFi manager window
            return True
        else:
            if password is None:
                # Use CTkInputDialog for a larger, customizable password input dialog
                dialog = ctk.CTkInputDialog(
                    text=f"Enter password for {ssid}:",
                    title="Password Required",
                    font=("Arial", 14)
                )
                dialog.geometry("400x200")  # Set custom size for the dialog
                password = dialog.get_input()  # Get the input from the dialog
                if not password:
                    return False

            profile = f"""<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                <name>{ssid}</name>
                <SSIDConfig><SSID><name>{ssid}</name></SSID></SSIDConfig>
                <connectionType>ESS</connectionType>
                <connectionMode>auto</connectionMode>
                <MSM><security>
                    <authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption>
                    <sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>{password}</keyMaterial></sharedKey>
                </security></MSM>
            </WLANProfile>"""
            profile_path = f"{ssid}.xml"
            with open(profile_path, "w") as file:
                file.write(profile)
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}", "user=current"], check=True)
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], check=True)
            messagebox.showinfo("Success", f"Connected to {ssid} successfully!")
            if root:
                root.destroy()  # Close the WiFi manager window
            return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to connect to {ssid}. Error: {e}")
        return False

def run_wifi_manager():
    """Run the WiFi Manager application."""
    # Create the root window
    root = ctk.CTk()
    root.title("WiFi Manager")
    root.geometry("500x500")

    def update_network_list():
        """Updates the list of available networks in the GUI."""
        for widget in network_frame.winfo_children():
            widget.destroy()  # Clear the current list
        networks = scan_wifi()
        for network in networks:
            network_label = ctk.CTkLabel(network_frame, text=network, font=("Arial", 16), cursor="hand2", anchor="w")
            network_label.pack(pady=2, fill=ctk.X)
            network_label.bind("<Double-Button-1>", lambda event, ssid=network: on_network_select(ssid))

    def update_wifi_status():
        """Updates the current WiFi status in the GUI."""
        status_text.configure(state="normal")
        status_text.delete(1.0, ctk.END)  # Clear the current status
        status_info = get_wifi_status()
        status_text.insert(ctk.END, f"SSID: {status_info.get('SSID', 'Not connected')}\n")
        status_text.insert(ctk.END, f"Status: {status_info.get('Status', 'Unknown')}\n")
        status_text.insert(ctk.END, f"Signal Strength: {status_info.get('Signal Strength', 'Unknown')}")
        status_text.configure(state="disabled")

    def on_network_select(ssid):
        """Handles network selection from the list."""
        if connect_to_wifi(ssid, root=root):
            root.destroy()  # Close the WiFi manager window on successful connection

    # Current WiFi status
    status_label = ctk.CTkLabel(root, text="Current WiFi Status:", font=("Arial", 16))
    status_label.pack(pady=10)

    status_text = ctk.CTkTextbox(root, height=100, width=400, font=("Arial", 15))
    status_text.pack(pady=10)
    status_text.configure(state="disabled")  # Make it read-only

    # Available networks
    network_label = ctk.CTkLabel(root, text="Available WiFi Networks:", font=("Arial", 16))
    network_label.pack(pady=10)

    # Use a CTkScrollableFrame for the network list
    network_frame = ctk.CTkScrollableFrame(root, width=400, height=150)
    network_frame.pack(pady=10)

    # Refresh button
    refresh_button = ctk.CTkButton(root, text="Refresh", command=lambda: [update_network_list(), update_wifi_status()], font=("Arial", 15))
    refresh_button.pack(pady=10)

    # Initial update
    update_network_list()
    update_wifi_status()

    # Start the Tkinter main loop
    root.mainloop()