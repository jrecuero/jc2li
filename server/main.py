import http.server


HOST_NAME = "0.0.0.0"
PORT_NUMBER = 5001


class CliHandler(http.server.BaseHTTPRequestHandler):
    pass


if __name__ == '__main__':
    httpd = http.server.HTTPServer((HOST_NAME, PORT_NUMBER), CliHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
