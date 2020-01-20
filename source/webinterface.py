from flask import Flask, Response, request
from waitress import serve
import netifaces as ni
import cv2
import os

def mdebug(value):
    DEBUG = False
    if DEBUG:
        print(value)

IP = '0.0.0.0'
PORT = 80
home_file = os.path.dirname(os.path.realpath(__file__)) + '/index.html'
vs = cv2.VideoCapture(0)
_chave = lambda:0
_chaveMedir = _chave
_gotas = _chave
_apagar = _chave
_salvar = _chave
app = Flask(__name__)


def inject_functions(chave, chaveMedir, gotas, apagar, salvar):
    global _chave
    global _chaveMedir
    global _gotas
    global _apagar
    global _salvar
    
    _chave = chave
    _chaveMedir = chaveMedir
    _gotas = gotas
    _apagar = apagar
    _salvar = salvar

@app.route('/')
def home():
    return Response(open(home_file, 'rb').read())

@app.route('/chave')
def chave():
    _chave()
    mdebug('Chave acionada.')
    return Response('OK.')

@app.route('/chaveMedir')
def chaveMedir():
    _chaveMedir(request.args.get('ddp'), request.args.get('divisions'))
    mdebug('Chave acionada com medida.')
    return Response('OK.')

@app.route('/gotas')
def gotas():
    _gotas()
    mdebug('Gotas acionada.')
    return Response('OK.')

@app.route('/apagar')
def apagar():
    _apagar()
    mdebug('Apagar acionado.')
    return Response('OK.')

@app.route('/salvar')
def salvar():
    filename = _salvar()
    mdebug('Salvar acionado.')
    return Response('OK.')

def generate():
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
def video_feed():
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

def getServerIPs():
    # Get server IP
    ips = []
    for iface in ni.interfaces():
        try:
            ips.append( ni.ifaddresses(iface)[ni.AF_INET][0]['addr'] )
        except Exception:
            pass
    return ips

def runserver():
    mdebug('Interface online')
    #app.run(host=IP, port=PORT, debug=True)  # To development
    serve(app, host=IP, port=PORT)