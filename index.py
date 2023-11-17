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
                question_open = False
                question_name = -1
                for line in form_stripped.split("\n"):
                    if line[0] == "=":
                        form_html += "<h1>" + line[1:].strip() + "</h1>"
                    elif line[0] == "*":
                        if question_open:
                            form_html += "</fieldset>"
                        question_open = True
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
                form_raw = open("./DATA/FORMS/"+self.path[9:]+".txt", "rt").read()
                form_stripped = html.escape(form_raw)
                form_stripped = form_stripped.split("\n")
                file_questions = open("./DATA/RESPONSES/"+self.path[9:]+".txt", "rt").read().split("!")
                for i in range(len(file_questions)):
                    file_questions[i] = file_questions[i].split("$")
                response_html = "<!DOCTYPE html><html><head><title>RESPONSES</title></head><body>"
                response_question_num = -1
                for line in form_stripped:
                    print(line)
                    if line[0] == "=":
                        response_html += "<h1>" + line[2:] + "</h1>"
                    elif line[0] == "*":
                        response_html += "<h2>" + line[2:] + "</h2>"
                        response_question_num += 1
                        response_answer_num = 0
                    elif line[0] == "-" or line[0] == "+":
                        response_html += "<p>" + line + "</p> <p>" + file_questions[response_question_num][response_answer_num] + "</p>"
                        response_answer_num += 1
                response_html += "</body></html>"
                self.wfile.write(bytes(response_html, "utf-8"))
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
            question_open = False
            form_response_data = ""
            for line in form_data.split("\n"):
                if line[0] == "*":
                    if question_open:
                        form_response_data += "!"
                    question_open = True
                    question_num = 0
                elif line[0] == "-" or line[0] == "+":
                    if question_num == 0:
                        form_response_data += "0"
                        question_num += 1
                    else:
                        form_response_data += "$0"
            form_uuid = uuid.uuid4().hex
            form_file = open("./DATA/FORMS/"+form_uuid+".txt", "w")
            form_response_file = open("./DATA/RESPONSES/"+form_uuid+".txt", "w")
            form_file.write(form_data)
            form_response_file.write(form_response_data)
            self._set_response()
            self.wfile.write(bytes("<html><head><title>Created</title></head><body>", "utf-8"))
            self.wfile.write(bytes("<h1>Your form has been created</h1>", "utf-8"))
            self.wfile.write(bytes("<p>View form: URL/take/%s</p>" % form_uuid, "utf-8"))
            self.wfile.write(bytes("<p>View results: URL/results/%s</p>" % form_uuid, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path.startswith("/submit"):
            answer_data = post_data.decode("utf-8").replace("+", " ").split("&")
            answers = []
            for answer in answer_data:
                answer_part = answer.split("=")
                for part in answer_part:
                    answers += [int(unquote(part))]
                    file_questions = open("./DATA/RESPONSES/"+self.path[8:]+".txt", "rt").read().split("!")
            for i in range(len(file_questions)):
                file_questions[i] = file_questions[i].split("$")
            for i in range(0, len(answers)-1, 2):
                file_questions[answers[i]][answers[i+1]] = str(int(file_questions[answers[i]][answers[i+1]]) + 1)
            for i in range(len(file_questions)):
                file_questions[i] = "$".join(file_questions[i])
            file_questions = "!".join(file_questions)
            form_response_file = open("./DATA/RESPONSES/"+self.path[8:]+".txt", "w")
            form_response_file.write(file_questions)
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