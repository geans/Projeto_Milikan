from flask import Flask, render_template, Response
from waitress import serve
import netifaces as ni
import cv2

app = Flask(__name__)

IP = '0.0.0.0'
PORT = 8080
home_file = 'index.html'
vs = cv2.VideoCapture(0)

@app.route('/')
def home():
    return Response(open(home_file, 'rb').read())

@app.route('/chave')
def chave():
    print('Chave acionada.')
    return Response('OK.')

@app.route('/chaveMedir')
def chaveMedir():
    print('Chave acionada com medida.')
    return Response('OK.')

@app.route('/gotas')
def gotas():
    print('Gotas acionada.')
    return Response('OK.')

@app.route('/apagar')
def apagar():
    print('Apagar acionado.')
    return Response('OK.')

@app.route('/salvar')
def salvar():
    print('Salvar acionado.')
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


if __name__ == '__main__':
    # Mostrar ips do servidor
    print()
    for iface in ni.interfaces():
        try:
            ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
            print('Executando em: http://{}:{}'.format(ip, PORT))
        except Exception:
            pass
    print()
        
    #app.run(host=IP, port=PORT, debug=True)  # To development
    serve(app, host=IP, port=PORT)


