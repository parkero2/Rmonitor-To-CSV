import socketserver
import flask
import threading
from main import positions

WSHOST, WSPORT, SOCKHOST, SOCKPORT = "127.0.0.1", 8080, "127.0.0.1", 9999

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())

class MyFlaskServer(threading.Thread):
    global WSHOST, WSPORT
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        self.app.run(host=WSHOST, port=WSPORT, debug=False)
        print("Flask server started")
    
app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html', positions=positions)

async def mainF():
    global app, SOCKHOST, SOCKPORT
    flask_server = MyFlaskServer(app)
    flask_server.start()

    with socketserver.TCPServer((SOCKHOST, SOCKPORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
        print("Socket server started")