from http.server import HTTPServer, CGIHTTPRequestHandler

PORT = 8000

if __name__ == '__main__':
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
    httpd.serve_forever()
