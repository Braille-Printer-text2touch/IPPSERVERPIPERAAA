from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import string
import subprocess

class IPPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST requests by echoing back the received data.
        """
        # Log the request path and headers
        print(f"Received POST request on path: {self.path}")

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print(f"Request Body: {body.decode('utf-8', errors='replace')}")

        # Send response
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        # self.wfile.write(json.dumps({"status": "Print job received", "file": job_filename}).encode('utf-8'))

        SPEECH = body.decode('utf-8', errors='replace')
        response_data = {
            "RECEIVED": SPEECH,
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        self.wfile.write(b'\n')

        # Save as a file
        fname = ''.join(random.choice(string.ascii_letters) for _ in range(9))
        print("rand file: ", fname, '\n')
        with open(fname, "w") as f:
            f.write(SPEECH)
        print(f"file probably saved--as {fname}")
        f = open(fname, "r")
        print(f.read())
        
        # Send the data to the actual ipp server
        print("Sending to actual ipp server")
        subprocess.run(["lp", "-d", "IPPAAAlocal", fname])

        # PIPING!!
        pipe_path = "/var/run/user/1000/text2touch_pipe"

        try:
            with open(pipe_path, "w") as pipe:
                # pipe.write("HERE ARE SOME WORDS: ")
                pipe.write(SPEECH)
        except FileExistsError:
            print("Named pipe already exists!")
        except OSError as e:
            print(f"Named pipe creation failed: {e}")

    def do_GET(self):
        """
        Handle GET requests for checking server status.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"IPPAAAlocal is running!\n")

def run(server_class=HTTPServer, handler_class=IPPRequestHandler, port=1002):
    """
    Run the IPP server on the specified port.
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    # zeroconf = advertise_printer(port)
    print(f"Starting IPP server on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # zeroconf.close()
        print("Shutting down IPP server")
    
if __name__ == "__main__":
    run()