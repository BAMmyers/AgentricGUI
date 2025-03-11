import http.server
import os

# Change to the directory containing the templates
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create server
server = http.server.HTTPServer(
    ('0.0.0.0', 8000), 
    http.server.SimpleHTTPRequestHandler
)

print("Server started at http://localhost:8000")
print("Open your browser to http://localhost:8000/templates/index.html")
server.serve_forever()
