from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import cv2
import os
import io
import sys
import numpy as np
import base64
from datetime import datetime
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from inference_sdk import InferenceHTTPClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit,send
import sys


app = Flask(__name__)
socketio = SocketIO(app,debug=True, cors_allowed_origins='*',async_mode='eventlet')
@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True )
    print('server received message' ,data)

from routes.classify_violence_one import upload_image_bp
from routes.post_student import upload_student_bp
from routes.classify_violence_many import upload_image_many_bp
from routes.signup import signup_bp
from routes.login import login_bp
from routes.post_video_violence import post_video_bp
from routes.swtich_post import switch_post_bp
from routes.switch_get import switch_get_bp
 
#app.register_blueprint(upload_image_bp)
app.register_blueprint(upload_student_bp)
app.register_blueprint(upload_image_many_bp)#done
app.register_blueprint(signup_bp)#done
app.register_blueprint(login_bp)#done
app.register_blueprint(post_video_bp)
app.register_blueprint(switch_post_bp)
app.register_blueprint(switch_get_bp)



if __name__ == '__main__':
    socketio.run(app, debug=True)
