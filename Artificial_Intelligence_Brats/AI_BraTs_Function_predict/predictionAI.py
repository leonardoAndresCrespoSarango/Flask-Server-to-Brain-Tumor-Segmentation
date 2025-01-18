
import os
import threading

from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
import numpy as np
from UNET import UNet
from H5 import load_hdf5_file
from graficas.graficasPloty import generate_graph1, generate_graph2, generate_graph3, generate_graph4, generate_graph5, \
    generate_graph6, generate_graph6_no_prediction

predictionBratsAI = Blueprint('predictionBratsAI', __name__)
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 3
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('model_3D\\3 clases\\modelUnet3D_3.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)
def delete_file_after_delay(file_path, delay):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")

    timer = threading.Timer(delay, delete_file)
    timer.start()
@predictionBratsAI.route('/predict-ia', methods=['POST'])
def predict_ia():
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    h5_filename = os.path.join('processed_files', f'{patient_id}.h5')

    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

    try:
        test_img = load_hdf5_file(h5_filename)
        if test_img is None:
            return jsonify({'message': 'Error al cargar el archivo HDF5.'}), 500

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # Generar las gráficas
        graph1_html = generate_graph1(test_img, test_prediction_argmax)
        graph2_html, report_text2 = generate_graph2(test_prediction_argmax)
        graph3_html = generate_graph3(test_img, test_prediction_argmax)
        graph4_html = generate_graph4(test_img, test_prediction_argmax)
        graph5_html, report_text5 = generate_graph5(test_img, test_prediction_argmax)
        graph6_html = generate_graph6(test_img, test_prediction_argmax)

        graph1_url = url_for('static', filename=graph1_html, _external=True)
        graph2_url = url_for('static', filename=graph2_html, _external=True)
        graph3_url = url_for('static', filename=graph3_html, _external=True)
        graph4_url = url_for('static', filename=graph4_html, _external=True)
        graph5_url = url_for('static', filename=graph5_html, _external=True)
        graph6_url = url_for('static', filename=graph6_html, _external=True)

        return jsonify({
            "html_url1": graph1_url,
            "html_url2": graph2_url,
            "html_url3": graph3_url,
            "html_url4": graph4_url,
            "html_url5": graph5_url,
            "html_url6": graph6_url,
            "report_text2": report_text2,
            "report_text5": report_text5
        })

    except Exception as e:
        print(f"Error durante la predicción: {str(e)}")
        return jsonify({"message": "Error durante la predicción. Consulta los registros del servidor para más detalles."}), 500
@predictionBratsAI.route('/generate-graph6', methods=['POST'])
def generate_graph6_route():
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    h5_filename = os.path.join('processed_files', f'{patient_id}.h5')

    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

    try:
        # Cargar las imágenes desde el archivo HDF5
        test_img = load_hdf5_file(h5_filename)
        if test_img is None:
            return jsonify({'message': 'Error al cargar el archivo HDF5.'}), 500

        # Generar la gráfica 6 (solo imágenes del paciente)
        graph6_html = generate_graph6_no_prediction(test_img)

        # Generar la URL para la gráfica
        graph6_url = url_for('static', filename=graph6_html, _external=True)

        return jsonify({
            "html_url6": graph6_url
        })

    except Exception as e:
        print(f"Error al generar la gráfica 6: {str(e)}")
        return jsonify({"message": "Error al generar la gráfica 6. Consulta los registros del servidor para más detalles."}), 500
