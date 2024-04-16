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

app.config['MONGO_URI'] = 'mongodb://localhost:27017/db'
mongo = MongoClient(app.config['MONGO_URI'])
boolean_variable_collection = mongo.db.boolean_variable

mongo = PyMongo(app)

switch_get_bp = Blueprint('get_variable', __name__)



@switch_get_bp.route('/get_variable', methods=['POST'])
def get_variable():
    data = request.get_json()

    # Ensure the 'value' and 'userid' keys are present in the JSON data
    if 'userid' not in data:
        return jsonify({'error': 'Missing "userid" parameter in the request'}), 400

    userid = data['userid']

    # Find the document with the provided userid
    variable_data = boolean_variable_collection.find_one({'userid': userid})

    # Check if document exists
    if variable_data:
        return jsonify({'variable': variable_data['value']})
    else:
        return jsonify({'error': 'No variable found for the provided userid'}), 404