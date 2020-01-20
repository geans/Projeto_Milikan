from flask import Flask, Response
from waitress import serve
import netifaces as ni
import cv2

app = Flask(__name__)

IP = '0.0.0.0'
PORT = 8080
home_file = 'index.html'
vs = cv2.VideoCapture(0)

def mdebug(value):
    print(value)
    #pass


class WebInterface:
    def __init__(self, _chave, _chaveMedir, _gotas, _apagar, _salvar):
        self._chave = _chave
        self._chaveMedir = _chaveMedir
        self._gotas = _gotas
        self._apagar = _apagar
        self._salvar = _salvar
        #app.run(host=IP, port=PORT, debug=True)  # To development
        serve(app, host=IP, port=PORT)

    def getServerIPs(self)
        # Get server IP
        ips = []
        for iface in ni.interfaces():
            try:
                ips.append( ni.ifaddresses(iface)[ni.AF_INET][0]['addr'] )
            except Exception:
                pass
        return ips
        
        
    @app.route('/')
    def home(self):
        return Response(open(home_file, 'rb').read())

    @app.route('/chave')
    def chave(self):
        self._chave()
        mdebug('Chave acionada.')
        return Response('OK.')

    @app.route('/chaveMedir')
    def chaveMedir(self):
        self._chaveMedir()
        mdebug('Chave acionada com medida.')
        return Response('OK.')

    @app.route('/gotas')
    def gotas(self):
        self._gotas()
        mdebug('Gotas acionada.')
        return Response('OK.')

    @app.route('/apagar')
    def apagar(self):
        self._apagar()
        mdebug('Apagar acionado.')
        return Response('OK.')

    @app.route('/salvar')
    def salvar(self):
        self._salvar()
        mdebug('Salvar acionado.')
        return Response('OK.')

    def generate(self):
        global vs
        # loop over frames from the output stream
        while True:
            ret, frame = vs.read()
            if ret:
                (flag, encodedImage) = cv2.imencode(".jpg", frame)
     
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encodedImage) + b'\r\n')
                
    @app.route("/video_feed")
    def video_feed(self):
        return Response(generate(),
            mimetype = "multipart/x-mixed-replace; boundary=frame")