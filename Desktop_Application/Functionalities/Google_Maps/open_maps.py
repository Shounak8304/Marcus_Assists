import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time

# Global variable to store location
location_data = None

class LocationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
                <body>
                    <script>
                        navigator.geolocation.getCurrentPosition(
                            (position) => {
                                fetch('/location', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                        latitude: position.coords.latitude,
                                        longitude: position.coords.longitude
                                    })
                                });
                            },
                            (error) => { console.log(error); }
                        );
                    </script>
                    <p>Location data is being sent...</p>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
            
    def do_POST(self):
        global location_data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        location_data = json.loads(post_data)
        self.send_response(200)
        self.end_headers()

def start_server():
    server = HTTPServer(('localhost', 8000), LocationHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

def get_current_location():
    global location_data
    server = start_server()
    
    print("Please visit: http://localhost:8000 in your browser to share your location.")
    
    for _ in range(10):  # Wait for 10 seconds
        if location_data:
            server.shutdown()
            return location_data
        time.sleep(1)

    server.shutdown()
    return {"latitude": 18.604072319693284, "longitude": 73.756311868149}

def open_maps(query):
    
    current_location_data = get_current_location()
    latitude = current_location_data["latitude"]
    longitude = current_location_data["longitude"]

    url = f"https://www.google.com/maps/dir/?api=1&origin={latitude},{longitude}&destination={query}"
    webbrowser.open(url)

