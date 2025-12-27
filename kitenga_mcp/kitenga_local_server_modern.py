from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import parse_qs

PORT = 8080
SAVE_FOLDER = os.path.expanduser("~/Desktop/the_terminal")
LOG_FILE = os.path.join(SAVE_FOLDER, "koreros_2025.txt")
os.makedirs(SAVE_FOLDER, exist_ok=True)

class KitengaHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            content_type = self.headers.get('Content-Type')
            boundary = content_type.split("boundary=")[-1].encode()
            remainbytes = int(self.headers['Content-Length'])

            line = self.rfile.readline()
            remainbytes -= len(line)
            if not boundary in line:
                self.send_error(400, "Content does not begin with boundary")
                return

            line = self.rfile.readline()  # Content-Disposition
            remainbytes -= len(line)
            filename = line.decode().split('filename=')[-1].strip().strip('"').replace("\\", "/").split("/")[-1]

            self.rfile.readline()  # Content-Type
            remainbytes -= len(line)

            self.rfile.readline()  # empty line
            remainbytes -= len(line)

            file_data = b""
            preline = self.rfile.readline()
            remainbytes -= len(preline)
            while remainbytes > 0:
                line = self.rfile.readline()
                remainbytes -= len(line)
                if boundary in line:
                    file_data += preline[:-1]  # remove trailing 

                    break
                file_data += preline
                preline = line

            filepath = os.path.join(SAVE_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(file_data)

            with open(LOG_FILE, 'a', encoding='utf-8') as log:
                log.write(f"[UPLOAD] {filename}\n")

            self._set_headers()
            self.wfile.write(json.dumps({'status': 'uploaded', 'filename': filename}).encode('utf-8'))

        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode('utf-8'))

            message = data.get('message', [''])[0]
            filename = data.get('filename', ['kitenga_entry.txt'])[0]

            file_path = os.path.join(SAVE_FOLDER, filename)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(message + '\n')

            self._set_headers()
            self.wfile.write(json.dumps({'status': 'saved', 'filename': filename}).encode('utf-8'))

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'message': 'Kitenga server is running'}).encode('utf-8'))

if __name__ == "__main__":
    print(f"Starting Kitenga local server on port {PORT}...")
    httpd = HTTPServer(('localhost', PORT), KitengaHandler)
    print("Server is live. Press CTRL+C to stop.")
    httpd.serve_forever()
