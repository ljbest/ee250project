
import cv2
from PIL import Image
import os
import time
from flask import Flask, Response, json, render_template
from werkzeug.utils import secure_filename
from flask import request
from flask_socketio import SocketIO, emit
from os import path, getcwd
import time
import os
import base64
import io

app = Flask(__name__,template_folder='./')
socketio = SocketIO(app, logge=True)

host_ip = "0.0.0.0"


cameras = {}

@app.route('/connect', methods=['POST'])
def connect():
    if request.is_json:
        data = request.get_json()
        name = data
        if name not in cameras:
            cameras[name] = request.remote_addr
            return f"register camera {name} with ip {cameras[name]}", 200
        else:
            return "name already exists", 400
    return "Invalid Request", 400
    
@app.route('/disconnect', methods=['POST'])
def disconnect():
    if request.is_json:
        data = request.get_json()
        name = data
        if name not in cameras:
            return f"{name} does not exist", 400
        else:
            del cameras[name]
            return f"removed {name} from cameras", 200
    return "Invalid Request", 400
    
@app.route('/camera')
def video_feed():
    return render_template('camera.html')
@app.route('/camera/list')
def print_cameras():
    return render_template('camera_list.html', camera_list=cameras)
    
@app.route('/camera/get', methods=['POST'])
def get_camera_image():
    if request.is_json:
        data = request.get_json()
        name = data["camera_name"]+'.jpg';
        with open(name, 'wb') as file:
            file.write(base64.decodebytes(bytes(data["image"][23:],'utf-8')))
        return "got image", 200
    return "Invalid Request", 400
app.run(host=host_ip, port=5000, debug=False, threaded=False,ssl_context='adhoc')
