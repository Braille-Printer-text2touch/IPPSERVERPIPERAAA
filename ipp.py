from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import posix

class IPPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST requests by echoing back the received data.
        """
        # Log the request path and headers
        print(f"Received POST request on path: {self.path}")
        print(f"Headers: {self.headers}")
        
        # Read the request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print(f"Request Body: {body.decode('utf-8', errors='replace')}")

        # Respond with the echoed data
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        SPEECH = body.decode('utf-8', errors='replace')
        response_data = {
            "received": SPEECH,
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

        # PIPING!!
        pipe_path = "/var/run/user/1000/text2type_pipe"

        # try:
        with open(pipe_path, "w") as pipe:
            pipe.write("HERE ARE SOME WORDS: ")
            pipe.write(SPEECH)
        # except FileExistsError:
        #     print("Named pipe already exists!")
        # except OSError as e:
        #     print(f"Named pipe creation failed: {e}")

    def do_GET(self):
        """
        Handle GET requests for checking server status.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"IPP Server is running!")

def run(server_class=HTTPServer, handler_class=IPPRequestHandler, port=1000):
    """
    Run the IPP server on the specified port.
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting IPP server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
