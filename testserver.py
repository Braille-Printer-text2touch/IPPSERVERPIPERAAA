from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os, posix
import struct
import socket
from zeroconf import ServiceInfo, Zeroconf

class IPPRequestHandler(BaseHTTPRequestHandler):
    
    def send_ipp_response(self, request_id, status_code=0x0000, attributes=b""):
        # """
        # Send a minimal IPP response.
        # """
        # response = struct.pack(">BBH", 1, 1, 0)  # IPP version 1.1, operation 1, request ID 0
        # response += struct.pack(">H", status_code)  # Status code (0x0000 = successful)
        # self.send_response(200)
        # self.send_header("Content-Type", "application/ipp")
        # self.end_headers()
        # self.wfile.write(response)
        """
        Send a structured IPP response with attributes.
        """
        response = struct.pack(">BBH", 2, 0, request_id)  # IPP version 2.0, operation 0, request ID
        response += struct.pack(">H", status_code)  # Status code (0x0000 = successful)
        response += attributes  # Append attributes (if any)
        response += b"\x03"  # End of attributes
        
        self.send_response(200)
        self.send_header("Content-Type", "application/ipp")
        self.end_headers()
        self.wfile.write(response)


    def do_POST(self):
        print(f"Received POST request on path: {self.path}")
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # print(f"Raw body (hex): {body.hex()}") # Log raw data for debug

        # Check if the request is an IPP request
        if self.headers.get("Content-Type") == "application/ipp":
            print(f"HEADERS: {self.headers}\n\n")
            try:
                # Extract/display first 8 bytes
                if len(body) < 8:
                    print("IPP req too short")
                    self.send_error(400, "Too-short req")
                    return

                # Unpack first 4 bytes
                # ipp_version, operation_id, request_id = struct.unpack(">BBH", body[:4])
                ipp_ver_maj, ipp_ver_min, operation_id, request_id = struct.unpack(">BBHI", body[:8])
                print(f"IPP Request - Version: {ipp_ver_maj}.{ipp_ver_min}, Operation: {operation_id}, Request ID: {request_id}")

                # Log full body if id is 0
                if operation_id == 0x0000:
                    print("Op ID is 0 (invalid) Full req body:")
                    print(body.hex())

                # Handle print job
                if operation_id == 0x000B:  # Print Job
                    print("Processing Print Job...")

                    # Save job file
                    # job_filename = f"/tmp/print_job_{request_id}.raw"
                    # with open(job_filename, "wb") as f:
                    #     f.write(body[4:])  # Store print data
                    # print(f"Print job saved as {job_filename}")

                    # SHOW CONTENTS!!!
                    content = body[8:].decode('utf-8', errors='replace')
                    print(f'CONTENTS:\n{content}')
                    
                    # Respond with "Job Received"
                    self.send_ipp_response(request_id, 0x0000)
                    return


                elif operation_id == 0x0002:  # Get-Printer-Attributes
                    print("CUPS requested printer status.")

                    # Create response attributes
                    attributes = b"\x01\x47"  # Operation attributes
                    attributes += b"\x47\x0Cprinter-state\x21\x01"  # printer-state = 3 (idle)
                    attributes += b"\x47\x10queued-job-count\x21\x00"  # No pending jobs

                    self.send_ipp_response(request_id, 0x0000, attributes)
                    return
                
                elif operation_id == 0x0004:  # Get-Job-Attributes
                    print("CUPS requested job status.")

                    attributes = b"\x01\x47"  
                    attributes += b"\x47\x0Ajob-state\x21\x04"  # job-state = 4 (completed)

                    self.send_ipp_response(request_id, 0x0000, attributes)
                    return
                
                else:
                    print("Unknown IPP operation")
                    self.send_ipp_response(request_id, 0x0501)  # Not supported
                    return
                
                # Send a basic IPP response to acknowledge the request
                # self.send_ipp_response(0x0000)  # 0x0000 = successful
                # return
            
            except struct.error:
                print("Invalid IPP request format")
                self.send_error(400, "Bad Request")
                return

        # If not an IPP request, handle as a normal POST request
        print(f'Not an IPP request, but a POST!')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Non-IPP POST request received"}).encode())


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
        "IPPAAAlocal._ipp._tcp.local.",  # Service name
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
    print(f"Printer advertised on the network as 'IPPAAAlocal'")
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
