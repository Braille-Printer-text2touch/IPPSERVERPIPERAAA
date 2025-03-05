from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os, posix
import struct
import socket
from zeroconf import ServiceInfo, Zeroconf

class IPPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handle POST requests by echoing back the received data.
        **and also (tries to) handle IPP requests!
        """
        # Log the request path and headers
        # print(f"Received POST request on path: {self.path}")
        # print(f"Headers: {self.headers}")
        
        # Read the request body
        # content_length = int(self.headers.get('Content-Length', 0))
        # body = self.rfile.read(content_length)
        # print(f"Request Body: {body.decode('utf-8', errors='replace')}")

        # Decode IPP headers from binary
        # try:
        #     ipp_version, operation_id, request_id = struct.unpack(">BBH", body[:4])
        #     print(f"IPP Version: {ipp_version}, Operation ID: {operation_id}, Request ID: {request_id}")
        # except struct.error:
        #     print("Invalid IPP request format")
        #     self.send_error(400, "Bad Request")
        #     return

        # Save the received print job data
        # job_filename = f"/tmp/print_job_{request_id}.raw"
        # with open(job_filename, "wb") as f:
        #     f.write(body[4:])  # Skip the IPP header and save the document data

        # print(f"Print job saved as {job_filename}")

        # Send response
        # self.send_response(200)
        # self.send_header("Content-Type", "application/json")
        # self.end_headers()
        # self.wfile.write(json.dumps({"status": "Print job received", "file": job_filename}).encode('utf-8'))

        # # Respond with the echoed data
        # self.send_response(200)
        # self.send_header("Content-Type", "application/json")
        # self.end_headers()

        # SPEECH = body.decode('utf-8', errors='replace')
        # response_data = {
        #     "RECEIVED": SPEECH,
        # }
        # self.wfile.write(json.dumps(response_data).encode('utf-8'))
        

        # PIPING!!
        # pipe_path = "/var/run/user/1000/text2type_pipe"

        # try:
        # with open(pipe_path, "w") as pipe:
        #     pipe.write("HERE ARE SOME WORDS: ")
        #     pipe.write(SPEECH)
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

def advertise_printer(port):
    """
    Advertise the IPP server as a network printer using mDNS/DNS-SD.
    """
    zeroconf = Zeroconf()

    # Define the printer service details
    service_info = ServiceInfo(
        "_ipp._tcp.local.",                 # Service type
        "IPPSERVERPIPERAAA._ipp._tcp.local.",  # Service name
        addresses=[socket.inet_aton("127.0.0.1")],  # Printer address
        port=port,                          # IPP port
        properties={
            "txtvers": "1",
            "qtotal": "1",
            "rp": "/",                      # Resource path for printing
            "ty": "Python IPP Printer",     # Human-readable printer type
            "adminurl": f"http://localhost:{port}",
            "note": "A virtual printer created in Python",
            "product": "(Python Printer)"
        },
        server="python-printer.local."      # Printer hostname
    )

    zeroconf.register_service(service_info)
    print(f"Printer advertised on the network as 'IPPSERVERPIPERAAA'")
    return zeroconf

def run(server_class=HTTPServer, handler_class=IPPRequestHandler, port=1000):
    """
    Run the IPP server on the specified port.
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    zeroconf = advertise_printer(port)
    print(f"Starting IPP server on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
        print("Shutting down IPP server and mDNS advertisement.")
    
if __name__ == "__main__":
    run()
