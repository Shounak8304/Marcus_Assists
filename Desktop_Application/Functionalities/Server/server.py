import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket, path):
    """Handles new client connections."""
    connected_clients.add(websocket)
    print(f"✅ A client connected! Total clients: {len(connected_clients)}")

    try:
        # Notify client of successful connection
        await websocket.send("Connected to server.")

        # Keep listening for messages from the client
        async for message in websocket:
            print(f"📩 Received from client: {message}")

    except websockets.exceptions.ConnectionClosed:
        print("❌ A client disconnected.")

    finally:
        connected_clients.remove(websocket)

async def send_commands():
    """Sends commands to all connected clients."""
    while True:
        if connected_clients:
            command = input("Enter command to send to all clients: ").strip()
            if command:
                print(f"📤 Sending command: {command}")
                await asyncio.gather(*(client.send(command) for client in connected_clients))
        else:
            print("⏳ Waiting for clients to connect...")
            await asyncio.sleep(5)

async def main():
    """Starts WebSocket server."""
    server = await websockets.serve(
        handle_client,
        "localhost",
        9001,
        ping_interval=30,  # Send pings every 30 seconds
        ping_timeout=300,  # Wait 300 seconds (5 minutes) for a pong response
    )
    print("🚀 WebSocket server started on ws://localhost:9001")

    # Run both the server and command sender concurrently
    await asyncio.gather(server.wait_closed(), send_commands())

if __name__ == "__main__":
    asyncio.run(main())