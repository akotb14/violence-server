from flask import Blueprint, jsonify, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.densenet import preprocess_input, decode_predictions
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

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://mcmohand888:33119765@security.aw8optf.mongodb.net/security'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
mongo = MongoClient(app.config['MONGO_URI'])
videos_collection = mongo.security.videos
mongo = PyMongo(app)

post_video_bp = Blueprint('post_video', __name__)

def post_video():
    #title = request.form.get('title')
    #date = request.form.get('date')
    #hour = request.form.get('hour')
    userid = request.form.get('userid')  # Extract userid from the request
 
    # Check if the request has the 'video' file
    if 'video' not in request.files or not  userid:
        return jsonify({'message': 'Invalid request'}), 400

    video_file = request.files['video']

    # Use secure_filename to ensure a secure filename
    video_filename = secure_filename(video_file.filename)

    # Save the video file
    if video_file:
        file_path = os.path.join('uploads/videos', video_filename)
        video_file.save(file_path)

        new_video = {
            'title': 'violence',
            'date': video_filename.split('_')[0],
            'hour': video_filename.split('_')[1].split('.')[0],
            'video_filename': video_filename,
            'userid': userid  
        }

        videos_collection.insert_one(new_video)

        return jsonify({'message': 'Video posted successfully'}), 201
    else:
        return jsonify({'message': 'Failed to save the video file'}), 500
    # Route for posting title, date, hour, and video file
@post_video_bp.route('/post_video', methods=['POST'])
def handle_post_video():
    return post_video()