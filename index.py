# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import time
import html
import uuid

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def form_creator(file):
        print(file)
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        self._set_response()
        try:
            if self.path == "/":
                self.wfile.write(open("./www/index.html", "rb").read())
            elif self.path == "/create":
                self.wfile.write(open("./www/create.html", "rb").read())
            elif self.path.startswith("/take"):
                self.wfile.write(bytes(form_creator(open(self.path, "rt").read())))
            elif self.path.startswith("/results"):
                print("results")
            else:
                self.wfile.write(open("./www/error.html", "rb").read())
        except:
            print("error")
            self.wfile.write(open("./www/error.html", "rb").read())
    def do_POST(self):
        print("post")
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length)
        form_data = post_data.decode("utf-8").replace("+", " ")
        form_data = unquote(form_data)
        form_data = form_data[4:]
        form_data = html.escape(form_data)
        
        uuid = uuid.uuid4()
        
        form_file = open("./DATA/"+uuid+".txt", "w")
        form_file.write(form_data)
        
        print(form_data)
        print(form_file)
        
        
        self._set_response()
        self.wfile.write(bytes("<html><head><title>Created</title></head><body>", "utf-8"))
        self.wfile.write(bytes("<h1>Your form has been created</h1>", "utf-8"))
        self.wfile.write(bytes("<p>View form: %s</p>" % "here", "utf-8"))
        self.wfile.write(bytes("<p>View results: %s</p>" % "there", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")