# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import time
import html
import uuid

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
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
                form_raw = open("./DATA/FORMS/"+self.path[6:]+".txt", "rt").read()
                form_stripped = html.escape(form_raw)
                form_html = "<!DOCTYPE html><html><head><title>FORM</title></head><body><form action='/submit/" + self.path[6:] + "' method='POST'>"
                question_open = False;
                question_name = -1
                for line in form_stripped.split("\n"):
                    if line[0] == "=":
                        form_html += "<h1>" + line[1:].strip() + "</h1>"
                    elif line[0] == "*":
                        if question_open:
                            form_html += "</fieldset>"
                        question_open = True;
                        question_name +=1
                        answer_value = 0
                        form_html += "<fieldset><h2>" + line[1:].strip() + "</h2>"
                    elif line[0] == "-":
                        form_html += "<label><input type=radio name='" + str(question_name) + "' value='" + str(answer_value) + "'/>" + line[1:].strip() + "</label><br/>"
                        answer_value += 1
                    elif line[0] == "+":
                        form_html += "<label><input type=checkbox name='" + str(question_name) + "' value='" + str(answer_value) + "'/>" + line[1:].strip() + "</label><br/>"
                        answer_value += 1
                form_html += "</fieldset><input type=submit></form></body></html>"
                self.wfile.write(bytes(form_html, "utf-8"))
            elif self.path.startswith("/results"):
                print("results")
            else:
                self.wfile.write(open("./www/error.html", "rb").read())
        except Exception as error:
            print("error: ", error)
            self.wfile.write(open("./www/error.html", "rb").read())
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if self.path == "/created":
            form_data = post_data.decode("utf-8").replace("+", " ")
            form_data = unquote(form_data)
            form_data = form_data[4:]
            form_data = html.escape(form_data)
            form_uuid = uuid.uuid4().hex
            form_file = open("./DATA/FORMS/"+form_uuid+".txt", "w")
            form_response_file = open("./DATA/RESPONSES/"+form_uuid+".txt", "w")
            form_file.write(form_data)
            self._set_response()
            self.wfile.write(bytes("<html><head><title>Created</title></head><body>", "utf-8"))
            self.wfile.write(bytes("<h1>Your form has been created</h1>", "utf-8"))
            self.wfile.write(bytes("<p>View form: URL/take%s</p>" % form_uuid, "utf-8"))
            self.wfile.write(bytes("<p>View results: URL/results%s</p>" % form_uuid, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path.startswith("/submit"):
            answer_data = post_data.decode("utf-8").replace("+", " ").split("&")
            answers = []
            for answer in answer_data:
                answer_part = answer.split("=")
                for part in answer_part:
                    try:
                        answers += [int(unquote(part))]
                    except:
                        print("Someone tried something funny")
            # CHANGE RESPONSES TO REFLECT NEW ANSWERS
            
            print(self.path[8:])
            print(answers)
            self._set_response()
            self.wfile.write(bytes("<html><head><title>Created</title></head><body><h1>submitted</h1></body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")