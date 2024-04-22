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

model = keras.models.load_model(r"D:\scu\Backend\MobileNetV2.h5")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://mcmohand888:33119765@security.aw8optf.mongodb.net/security'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
mongo = MongoClient(app.config['MONGO_URI'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

upload_image_bp = Blueprint('upload', __name__)

def classify_image(file_path):
    
    class_label = ['non-violence' , 'violence']
    # Load and preprocess the image
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    # Make predictions
    predictions = model.predict(img_array)

    
    result = class_label[np.argmax(predictions)]

    return result

@upload_image_bp.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(r'I:\MODELS\Backend2\Backend\uploads', filename)
        file.save(file_path)

        # Now you can send the image to your machine learning model for processing
        result = classify_image(file_path)

        return jsonify({'result': result})

    return jsonify({'error': 'File not allowed'})