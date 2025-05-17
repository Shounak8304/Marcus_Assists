# connect_to_server.py

import asyncio
import websockets

async def connect_to_server():
    max_retries = 5  # Maximum number of retries
    retry_interval = 10  # Seconds to wait before each retry
    retry_count = 0  # Initialize retry count

    while retry_count < max_retries:
        try:
            async with websockets.connect("ws://localhost:8765", max_size=None) as websocket:
                print("Connected to server.")
                await websocket.send("Client connected")  # Send initial message to server
                
                server_message = await websocket.recv()  # Receive acknowledgment from server
                if server_message == "Server connected":
                    print("Server connected. Ready to receive commands.")
                    return websocket  # Return the websocket object for future communication
                
            retry_count = 0  # Reset retry count on successful connection
        except websockets.exceptions.ConnectionClosedError:
            print("Server disconnected. Reconnecting...")
            retry_count += 1
            await asyncio.sleep(retry_interval)
        except Exception as e:
            print(f"Error: {str(e)}")
            break

    print("Server not available. Closing program.")
    return None  # Indicate failure to connect
