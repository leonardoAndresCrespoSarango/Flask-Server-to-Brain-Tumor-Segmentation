import io
import os
import sys
import imageio
import joblib
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv3D, Conv3DTranspose, Dropout, MaxPooling3D, concatenate
from UNET import dice_coef
from UNET import dice_coef_edema
from UNET import dice_coef_necrotic
from UNET import dice_coef_enhancing
from UNET import precision
from UNET import sensitivity
from UNET import specificity
from UNET import UNet
from H5 import load_hdf5_file
from moviepy.editor import ImageSequenceClip
from transformation_nifti_file_to_h5 import transform_and_predict
app = Flask(__name__)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
# Define las funciones de métricas personalizadas
# Cargar el pipeline y el modelo# Directorio temporal para archivos cargados
TEMP_DIR = 'temp/'
# Crear el modelo y cargar los pesos
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 4
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/model_3D/Final/modelUnet3D.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para manejar la predicción
@app.route('/predict', methods=['POST'])
def predict():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    try:
        # Asegurarse de que se envió un archivo
        if 'file' not in request.files:
            return "No se envió ningún archivo."

        file = request.files['file']
        file_path = os.path.join(TEMP_DIR, "temp_file.h5")
        file.save(file_path)

        # Ejecutar el pipeline y realizar la predicción
        video_filename = transform_and_predict(file_path, TEMP_DIR)

        if video_filename:
            # Redirigir a la página de resultados
            return redirect(url_for('result', video_filename=os.path.basename(video_filename)))

        return "Error durante la predicción."

    except Exception as e:
        print("Error durante la predicción:", str(e))
        return "Error durante la predicción. Consulta los registros del servidor para más detalles."

@app.route('/result')
def result():
    video_filename = request.args.get('video_filename')
    video_url = url_for('static', filename=video_filename)
    print(f"Video URL: {video_url}")
    return render_template('result.html', video_url=video_url)

if __name__ == "__main__":
    app.run(debug=True)