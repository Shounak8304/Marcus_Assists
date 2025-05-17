import os
import platform
import psutil
import cpuinfo
import customtkinter as ctk

def format_heading(title):
    return f"\n{'-'*20} {title} {'-'*20}\n"

def get_all_info():
    uname = platform.uname()
    cpu_info = cpuinfo.get_cpu_info()
    freq = psutil.cpu_freq()
    virtual_mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    partitions = psutil.disk_partitions()
    net_io = psutil.net_io_counters()
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    temps = None
    try:
        temps = psutil.sensors_temperatures()
    except AttributeError:
        pass

    info = (
        format_heading("System Info") +
        f"System: {uname.system}\n"
        f"Node Name: {uname.node}\n"
        f"Release: {uname.release}\n"
        f"Version: {uname.version}\n"
        f"Machine: {uname.machine}\n"
        f"Processor: {uname.processor}\n\n"

        + format_heading("CPU Info") +
        f"CPU Brand: {cpu_info['brand_raw']}\n"
        f"Architecture: {cpu_info['arch']}\n"
        f"Bits: {cpu_info['bits']}-bit\n"
        f"Logical Cores: {psutil.cpu_count(logical=True)}\n"
        f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
        f"Max Frequency: {freq.max:.2f} MHz\n"
        f"Current Frequency: {freq.current:.2f} MHz\n"
        f"CPU Usage: {psutil.cpu_percent(interval=0.5)}%\n\n"

        + format_heading("RAM Info") +
        f"Total RAM: {virtual_mem.total / (1024 ** 3):.2f} GB\n"
        f"Available RAM: {virtual_mem.available / (1024 ** 3):.2f} GB\n"
        f"Used RAM: {virtual_mem.used / (1024 ** 3):.2f} GB\n"
        f"RAM Usage Percentage: {virtual_mem.percent}%\n\n"

        + format_heading("Swap Memory") +
        f"Total Swap: {swap.total / (1024 ** 3):.2f} GB\n"
        f"Used Swap: {swap.used / (1024 ** 3):.2f} GB\n"
        f"Free Swap: {swap.free / (1024 ** 3):.2f} GB\n"
        f"Swap Usage Percentage: {swap.percent}%\n\n"

        + format_heading("Disk Info")
    )
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            info += (
                f"Device: {partition.device}\n"
                f"Mountpoint: {partition.mountpoint}\n"
                f"File System Type: {partition.fstype}\n"
                f"Total Size: {partition_usage.total / (1024 ** 3):.2f} GB\n"
                f"Used: {partition_usage.used / (1024 ** 3):.2f} GB\n"
                f"Free: {partition_usage.free / (1024 ** 3):.2f} GB\n"
                f"Usage Percentage: {partition_usage.percent}%\n\n"
            )
        except PermissionError:
            info += "Permission denied for this partition.\n"

    info += (
        format_heading("Network Info") +
        f"Bytes Sent: {net_io.bytes_sent / (1024 ** 2):.2f} MB\n"
        f"Bytes Received: {net_io.bytes_recv / (1024 ** 2):.2f} MB\n\n"
    )

    if battery:
        info += (
            format_heading("Battery Info") +
            f"Battery Percentage: {battery.percent}%\n"
            f"Power Plugged In: {battery.power_plugged}\n"
            f"Time Left: {battery.secsleft / 60:.2f} minutes\n\n"
        )
    else:
        info += format_heading("Battery Info") + "No battery detected.\n\n"

    if temps:
        info += format_heading("Temperature Info")
        for name, entries in temps.items():
            info += f"Sensor: {name}\n"
            for entry in entries:
                info += (
                    f"{entry.label or name}: {entry.current}°C (High: {entry.high}°C, Critical: {entry.critical}°C)\n"
                )
    else:
        info += format_heading("Temperature Info") + "Temperature monitoring is not supported on this system.\n\n"

    return info

def show_system_status():
    """Shows the system status in a GUI window."""
    root = ctk.CTk()
    root.title("MARCUS INTEL")
    root.geometry("900x700")

    frame_right = ctk.CTkFrame(root)
    frame_right.pack(padx=20, pady=20, fill="both", expand=True)

    text_widget_info = ctk.CTkTextbox(frame_right, wrap="word", font=("Courier", 18), height=20)
    text_widget_info.pack(padx=10, pady=10, fill="both", expand=True)

    text_widget_info.insert("end", get_all_info())

    # Run the Tkinter event loop in a non-blocking way
    def update():
        root.update_idletasks()
        root.update()
        if root.winfo_exists():
            root.after(100, update)  # Schedule the next update

    root.after(100, update)  # Start the update loop
    return root

def close_system_status(root):
    """Closes the system status GUI window."""
    if root is not None and root.winfo_exists():
        root.destroy()