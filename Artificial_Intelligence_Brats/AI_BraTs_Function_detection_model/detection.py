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

from DataBase import get_db_connection

# Configuración del Blueprint para manejar rutas relacionadas con la deteccion
detectionBratsAI = Blueprint('detectionBratsAI', __name__)

@detectionBratsAI.route('/detection-ai', methods=['POST'])
def detect_ia():
    # if 'user_id' not in session:
    #     return jsonify({"message": "Usuario no autenticado"}), 401
    
    # user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400
    
    
    
    
    ## realizar la clasificacion
    model = cargar_modelo_clasificacion()

    # Ruta del archivo HDF5
   
    h5_clasification_file = f"processed_files/{patient_id}_to_classify.h5"

    print(f"clasificando  con pacient {patient_id}")
    # Cargar el archivo
    with h5py.File(h5_clasification_file, 'r') as hf:
        h5_classification = np.array(hf['images'])  

    h5_classification = np.expand_dims(h5_classification, axis=0)
    # Imprimir dimensiones
    print("Dimensiones de h5_classification:", h5_classification.shape)

    # Realizar la predicción
    pred = model.predict(h5_classification)
    prob = pred[0][0]
    
     
    print(f"Predicción de clasificación: {prob:.2f}")

    # guardar en base de datos
    save_classification(round(float(prob), 2), patient_id)


    return jsonify({'message': round(float(prob), 2)})
        



# funcion que carga el modelo 
def cargar_modelo_clasificacion():
    classification_model_path = "model_classification/classification_brats_model_cnn.h5"
    
    classification_model = load_model(classification_model_path)

    return classification_model



# metodo para guardar la prediccion/clasificacion en la base de datos

def save_classification(prediccion, patient_id):
    try:
        # Convertir el resultado de la predicción a booleano (1 -> True, 0 -> False)
        cancer_prediction = bool(round(float(prediccion)))  # Redondea para garantizar valores 0 o 1

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Actualizar la tabla 'diagnostics' con la predicción
        cursor.execute("""
            UPDATE diagnostics
            SET cancer_prediction = %s
            WHERE patient_id = %s;
        """, (cancer_prediction, patient_id))

        # Confirmar la transacción
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Predicción guardada en la base de datos para el paciente {patient_id}: {cancer_prediction}")

    except Exception as e:
        print(f"Error al guardar la predicción en la base de datos: {e}")


