import http.server
import urllib.parse
import time
import loggerator
from examples.commands import CliCommands


HOST_NAME = "0.0.0.0"
PORT_NUMBER = 5001
MODULE = 'CLI.server'
LOGGER = loggerator.getLoggerator(MODULE)


class CliHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        LOGGER.display('url: {0}'.format(url), color='YELLOW')
        LOGGER.display('path: {0}'.format(url.path), color='YELLOW')
        LOGGER.display('query: {0}'.format(url.query), color='YELLOW')
        LOGGER.display('query as dict: {0}'.format(urllib.parse.parse_qs(url.query)), color='YELLOW')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('Cli Server up and running', 'utf8'))
        app = urllib.parse.parse_qs(url.query)['app']
        command = urllib.parse.parse_qs(url.query)['command']
        LOGGER.display('app: {0} command: {1}'.format(app, command), color='YELLOW')
        self.server.cli.exec_user_input(command[0])
        return


class CliServer(http.server.HTTPServer):

    def __init__(self, host_and_port, handler):
        super(CliServer, self).__init__(host_and_port, handler)
        self.cli = CliCommands()


if __name__ == '__main__':
    httpd = CliServer((HOST_NAME, PORT_NUMBER), CliHandler)
    LOGGER.display('{0} Server Starts - {1}:{2}'.format(time.asctime(), HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    LOGGER.display('\n{0} Server Stops - {1}:{2}'.format(time.asctime(), HOST_NAME, PORT_NUMBER))
