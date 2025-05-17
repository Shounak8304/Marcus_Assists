import asyncio
import websockets
import threading
import base64
import os
import wave
import webbrowser
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
import speech_recognition as sr
from number_parser import parse

connected_clients = set()
android_client = None
desktop_client = None


class AudioProcessor:
    def __init__(self):
        self.output_dir = "received_audio"
        self.recognizer = sr.Recognizer()
        os.makedirs(self.output_dir, exist_ok=True)
        print("🌟 Audio Processor Ready")

    def save_as_wav(self, audio_data, filepath, sample_rate=8000, channels=1):
        try:
            with wave.open(filepath, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data)
            print(f"💾 Audio saved as {filepath}")
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            raise

    def audio_to_text(self, filepath):
        try:
            with sr.AudioFile(filepath) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language="en-US")
                return text
        except sr.UnknownValueError:
            return "❌ Could not understand audio"
        except sr.RequestError as e:
            return f"❌ API unavailable: {e}"
        except Exception as e:
            return f"❌ Processing error: {e}"


audio_processor = AudioProcessor()


def normalize_numbers(text):
    try:
        parsed = parse(text)
        return parsed
    except Exception as e:
        print(f"⚠ Number parsing failed: {e}")
        return text


# ================================ WebSocket Handler ================================
async def handle_client(websocket):
    global android_client, desktop_client
    connected_clients.add(websocket)
    print(f"✅ New client connected! Total: {len(connected_clients)}")

    audio_buffer = bytearray()
    sample_rate = 8000
    channels = 1

    try:
        await websocket.send("Connected to Unified Server.")

        async for message in websocket:
            if isinstance(message, str):
                if message.lower() == "hello from android!":
                    android_client = websocket
                    await broadcast("android_connected", exclude=websocket)
                    print("🟢 Android connected")
                elif message.lower() == "marcus is connected!":
                    desktop_client = websocket
                    await broadcast("desktop_connected", exclude=websocket)
                    print("🔵 Desktop connected")
                elif message.startswith("AUDIO_BASE64:"):
                    try:
                        decoded = base64.b64decode(message.split(":", 1)[1])
                        filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                        filepath = os.path.join(audio_processor.output_dir, filename)
                        audio_processor.save_as_wav(decoded, filepath, sample_rate, channels)
                        transcription = audio_processor.audio_to_text(filepath)
                        normalized_transcription = normalize_numbers(transcription)
                        print(f"💬 Transcribed (normalized): {normalized_transcription}")
                        await send_to_android_and_desktop(f"TRANSCRIPTION:{normalized_transcription}")
                    except Exception as e:
                        err = f"❌ Failed to process Base64 audio: {e}"
                        print(err)
                        await websocket.send(f"ERROR:{err}")
                else:
                    await broadcast(message, exclude=websocket)
                    print(f"📩 Broadcasted message: {message}")

            elif isinstance(message, bytes):
                audio_buffer.extend(message)
                print(f"📥 Receiving binary audio: {len(audio_buffer)} bytes", end="\r")

                if len(audio_buffer) >= sample_rate * 2 * 5:  # 5 seconds of audio
                    try:
                        filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                        filepath = os.path.join(audio_processor.output_dir, filename)
                        audio_processor.save_as_wav(audio_buffer, filepath, sample_rate, channels)
                        transcription = audio_processor.audio_to_text(filepath)
                        normalized_transcription = normalize_numbers(transcription)
                        print(f"\n💬 Transcribed (normalized): {normalized_transcription}")
                        await send_to_android_and_desktop(f"TRANSCRIPTION:{normalized_transcription}")
                    except Exception as e:
                        err = f"❌ Failed to process binary audio: {e}"
                        print(err)
                        await websocket.send(f"ERROR:{err}")
                    audio_buffer = bytearray()

    except websockets.exceptions.ConnectionClosed:
        print("❌ A client disconnected.")
    except Exception as e:
        print(f"❌ Error in handle_client: {e}")
    finally:
        connected_clients.discard(websocket)  # Use discard to avoid KeyError
        if websocket == android_client:
            android_client = None
            print("⚠ Android client disconnected.")
            await broadcast("android_disconnected")
        if websocket == desktop_client:
            desktop_client = None
            print("⚠ Desktop client disconnected.")
            await broadcast("desktop_disconnected")
        print(f"⚠ Remaining clients: {len(connected_clients)}")


async def send_to_android_and_desktop(message):
    if message.startswith("TRANSCRIPTION:"):
        command = message.split("TRANSCRIPTION:", 1)[1]
    else:
        command = message

    if android_client:
        try:
            print(f"📲 Sending to Android: {command}")
            await android_client.send(command)
        except Exception as e:
            print(f"⚠ Failed to send to Android: {e}")

    if desktop_client:
        try:
            print(f"💻 Sending to Desktop: {command}")
            await desktop_client.send(command)
        except Exception as e:
            print(f"⚠ Failed to send to Desktop: {e}")


# ================================ Broadcast Utility ================================
async def broadcast(message, exclude=None):
    global android_client, desktop_client  # Declare globals at the start
    disconnected_clients = set()
    for client in connected_clients:
        if client != exclude:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                print(f"⚠ Failed to broadcast to client: {e}")

    # Clean up disconnected clients
    for client in disconnected_clients:
        connected_clients.discard(client)
        if client == android_client:
            android_client = None
            print("⚠ Android client disconnected during broadcast.")
        if client == desktop_client:
            desktop_client = None
            print("⚠ Desktop client disconnected during broadcast.")


# ================================ HTTP Server ================================
class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=self.directory, **kwargs)


def start_http_server():
    PORT = 8000
    server = HTTPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler)
    print(f"🌐 HTTP server running on http://0.0.0.0:{PORT}")
    server.serve_forever()


# ================================ WebSocket Entry ================================
async def start_websocket():
    print("🚀 Starting WebSocket server...")
    async with websockets.serve(handle_client, "0.0.0.0", 9001):
        print("🟢 WebSocket server running at ws://0.0.0.0:9001")
        await asyncio.Future()  # run forever


# ================================ Entry Point ================================
if __name__ == "__main__":
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True
    http_thread.start()
    webbrowser.open("http://0.0.0.0:8000")

    try:
        asyncio.run(start_websocket())
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down.")