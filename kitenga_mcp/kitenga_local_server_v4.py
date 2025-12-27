import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

UPLOAD_DIR = os.path.expanduser("~/Desktop/the_terminal")

class KitengaUploadHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(b"{\"status\": \"ok\", \"message\": \"Server is running\"}")

    def do_POST(self):
        if self.path != '/upload':
            self._set_headers(404)
            self.wfile.write(json.dumps({"status": "error", "message": "Not Found"}).encode('utf-8'))
            return

        content_length = int(self.headers['Content-Length'])
        boundary = self.headers['Content-Type'].split("boundary=")[1].encode()
        data = self.rfile.read(content_length)

        uploaded = False
        parts = data.split(b"--" + boundary)
        for part in parts:
            if b'Content-Disposition' in part and b'filename=' in part:
                headers, file_data = part.split(b"\r\n\r\n", 1)
                file_data = file_data.rsplit(b"\r\n", 1)[0]

                for header_line in headers.split(b"\r\n"):
                    if b"filename=" in header_line:
                        filename = header_line.split(b"filename=")[1].strip(b'"')
                        filepath = os.path.join(UPLOAD_DIR, filename.decode())
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        print(f"[UPLOAD] {filename.decode()} saved to {filepath}")
                        uploaded = True

        if uploaded:
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Upload successful"}).encode('utf-8'))
        else:
            self._set_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "Upload failed"}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=KitengaUploadHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Kitenga Upload Server v4 running on port {port}... Files will now respect subfolders like 'ocr/'.")
    httpd.serve_forever()

if __name__ == "__main__":
    run()