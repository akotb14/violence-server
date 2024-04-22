from flask import Blueprint, jsonify, request
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
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
import face_recognition
from ultralytics import YOLO

model = keras.models.load_model(r"D:\scu\Backend\MobileNetV2.h5")
model_object_detection = YOLO(r"D:\scu\Backend\best5.pt")
model_weapon_detection = YOLO(r"D:\scu\Backend\best8.pt")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://mcmohand888:33119765@security.aw8optf.mongodb.net/security'
#app.config['UPLOADED_PHOTOS_DEST'] = r'D:\scu\Backend1\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo = MongoClient(app.config['MONGO_URI'])
upload_image_many_bp = Blueprint('uploads', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
mongo = PyMongo(app)

def get_data():
    # Query MongoDB to retrieve data
    db = mongo.db
    collection = db['students']
    data = list(collection.find({}))
    known_face_encodings = []
    images = [doc['image'] for doc in data if 'image' in doc]
 
    for image in images:
        known_face_encodings.append(np.array(image ,dtype=np.float64))

    names = [doc['_id'] for doc in data if '_id' in doc]
    return (known_face_encodings ,names )

def face_detect(image_unkown):
    db = mongo.db
    collection = db['students']
    known_face_encodings , known_faces_names  = get_data()
    unknown_image = face_recognition.load_image_file(image_unkown)
    name = "unknown"
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

        matches = face_recognition.compare_faces(
            known_face_encodings, face_encoding)
        

        face_distance = face_recognition.face_distance(
            known_face_encodings, face_encoding)

        best_match_index = np.argmin(face_distance)

        if matches[best_match_index]:
            name = known_faces_names[best_match_index]
            data = collection.find_one({'_id':name})
            return data
    #print(data)
    return name
#face_detect(r'C:\Users\ahmed\OneDrive\Desktop\face_detection\un_known\500.jpg')

#load model of object detection
def object_detection_fun(file_path):
    try:
        img = image.load_img(file_path)
        img_array = image.img_to_array(img)
        if img_array.dtype != 'uint8':
            img_array = img_array.astype('uint8')  # Ensure image array is of type uint8
        results = model_object_detection.track(img_array, persist=True)
        is_track = results[0].boxes.cpu().numpy().is_track
        if is_track:
            return True
        else:
            return False
    except Exception as e:
        print('Error' + str(e))

def weapon_detection_fun(file_path):
    try:
        img = image.load_img(file_path)
        img_array = image.img_to_array(img)
        if img_array.dtype != 'uint8':
            img_array = img_array.astype('uint8')  # Ensure image array is of type uint8
        results = model_weapon_detection.track(img_array, persist=True)
        resultM = set(results[0].boxes.cpu().numpy().cls)

        if 0 in resultM:
           return True
        else:
            return False
    except Exception as e:
        print('Error' + str(e))

def classify_image(file_path):
     # Load your trained model
    class_label = ['non-violence' , 'violence']
    # Load and preprocess the image
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    #img_array = preprocess_input(img_array)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    # Make predictions
    predictions = model.predict(img_array)
    # # Classify as violence if the probability is above a certain threshold (adjust as needed)
    # threshold = 0.5
    result = class_label[np.argmax(predictions)]
    return result

@upload_image_many_bp.route('/uploads', methods=['POST'])
def upload_files():
    # Check if the POST request has the file part
    feature = request.form.to_dict()
    received_files = request.files.to_dict()
    if not feature:
            return jsonify({'error': 'No feature part'}) 
    # Check if the POST request has the file part
    if 'file' not in received_files:
        return jsonify({'error': 'No file part'})

    files = request.files.getlist('file')
        
        # If the user does not select any file
    if not files:
        return jsonify({'error': 'No selected file'})

    resultViolence = []
    resultNonViolence = []

    count_object = 0
    count_weapon = 0

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            #1-human -> violence -> face
            if(feature['object_detection'] == 'True'):
                is_object = object_detection_fun(file_path)
                if is_object:
                    count_object +=1

            if feature['object_detection'] == 'False' or is_object:
                if(feature['weapon_detection'] == 'True'):
                    is_weapon = weapon_detection_fun(file_path)
                    if is_weapon:
                        count_weapon +=1

                result = classify_image(file_path)
                if result == 'non-violence':
                    resultNonViolence.append(result)
                elif result == 'violence':
                    #face detection
                    resultViolence.append(result)
                if feature['face_detection'] == 'True':
                    if is_weapon or (result == 'violence'):
                            data = face_detect(file_path)
                            print(data)

        else:
            return jsonify({'error': 'One or more files not allowed'})
    print("violence",len(resultViolence) )
    print("nonviolence",len(resultNonViolence) )
    # check if there are objects or not
    if feature['object_detection'] == 'True':
        if count_object >=5 :
            if len(resultViolence) >= len(resultNonViolence) or count_weapon >=5: 
                return jsonify({'result': resultViolence[0] , 'isobject':True})
            else :
                return jsonify({'result': resultNonViolence[0] , 'isobject':True})
        else : 
            return jsonify({'result': 'non-violence' ,'isobject':False})
        
    else:
        if len(resultViolence) >= len(resultNonViolence) or count_weapon >=5:
            return jsonify({'result': resultViolence[0] , 'isobject':False})
        else:
            return jsonify({'result': resultNonViolence[0] , 'isobject':False})
    