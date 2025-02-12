# Funcion para deteccion de tumores
# El modelo de clasificacion que se carga es para predecir si el paciente tiene cancer cerebrar o no
# Despues de esto se manda a usar el modelo de segmentacion 

import os
import threading
import sys
import h5py
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint, current_app
import numpy as np
from UNET import UNet
from H5 import load_hdf5_file
from graficas.graficasPloty import generate_graph1, generate_graph2, generate_graph3, generate_graph4, generate_graph5, \
    generate_graph6, generate_graph6_no_prediction, generate_graphDiagnostic,  \
     generate_graph_real_and_predicted_segmentation_with_brain
import nibabel as nib
from skimage.transform import resize
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Conv3DTranspose
from tensorflow.keras.models import load_model


# Configuración del Blueprint para manejar rutas relacionadas con la deteccion
detectionBratsAI = Blueprint('detectionBratsAI', __name__)

@detectionBratsAI.route('/detection-ai', methods=['POST'])
def detect_ia():
    # if 'user_id' not in session:
    #     return jsonify({"message": "Usuario no autenticado"}), 401
    
    # user_id = session['user_id']
    # patient_id = request.json.get('patient_id')

    # if not patient_id:
    #     return jsonify({'message': 'Patient ID is missing'}), 400
    
    return jsonify({"message": "endpoint para deteccion clasificacion funcionando"}), 200
    

# funciones para realizar la clasificacion 

# funcion que carga el modelo 
def cargar_modelo_clasificacion():
    classification_model_path = "model_classification/classification_brats_model_cnn.h5"
    # dimesiones que acepta el modelo
    expected_shape = (128, 128, 128)
    classification_model = load_model(classification_model_path)

    patient_files = [os.path.join()]


# carga desde la base de datos el path de las modalidades
def get_patient_files():
    pass

def realizar_clasificacion():
    pass


def load_nifti(file_path):
    return nib.load(file_path).get_fdata()


# Obtener nombres de archivos de modalidades, los paths de la modalidades se guardan en 
# la base de datos
def get_modalities(patient_files):
    modalities = {}
    for file in patient_files:
        file_lower = file.lower()
        if 't1' in file_lower and 't1c' not in file_lower:
            modalities['T1'] = file
        elif 't1c' in file_lower:
            modalities['T1c'] = file
        elif 't2w' in file_lower:
            modalities['T2W'] = file
        elif 't2f' in file_lower:
            modalities['T2F'] = file
    return modalities


# Normalizar las imágenes con MinMaxScaler
def normalize(image):
    scaler = MinMaxScaler()
    return scaler.fit_transform(image.reshape(-1, image.shape[-1])).reshape(image.shape)


# Guardar imágenes en formato HDF5
def save_h5(filename, data):
    with h5py.File(filename, 'w') as hf:
        hf.create_dataset('image', data=data)


