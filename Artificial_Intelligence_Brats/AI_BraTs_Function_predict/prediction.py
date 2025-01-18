import threading
import os
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
import numpy as np
import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from DataBase import create_tables, get_db_connection
from H5 import load_hdf5_file
from moviepy.editor import ImageSequenceClip
import psycopg2

from UNET import UNet
from latex.plantilla import create_medical_report


predictionBrats = Blueprint('predictionBrats', __name__)
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
@predictionBrats.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        # Verificar el tipo de contenido de la solicitud
        if request.content_type != 'application/json':
            return jsonify({"error": "Tipo de contenido no soportado"}), 415

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        patient_info = {
            'name': data['name'],
            'age': data['age'],
            'gender': data['gender'],
            'id': data['patientId']
        }

        prediagnosis = data['diagnosis']

        folder_path = "processed_files/"
        hdf5_files = glob.glob(os.path.join(folder_path, "*.h5"))

        if not hdf5_files:
            return jsonify({"error": "No se encontraron archivos HDF5 en la carpeta especificada."}), 404

        file_path = hdf5_files[0]

        if not os.path.isfile(file_path):
            return jsonify({"error": "Archivo HDF5 no encontrado."}), 404

        test_img = load_hdf5_file(file_path)
        if test_img is None:
            return jsonify({"error": "Error al cargar el archivo HDF5."}), 500

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        images = []

        for i in range(test_prediction_argmax.shape[2]):
            fig, ax = plt.subplots(1, 2, figsize=(12, 8))

            ax[0].imshow(test_img[:, :, i, 1], cmap='gray')
            ax[0].title.set_text('Testing Image')

            ax[1].imshow(test_prediction_argmax[:, :, i])
            ax[1].title.set_text('Prediction on test image')

            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            plt.close(fig)

            images.append(image)

            temp_image_path = f"static/temp_image_{i}.png"
            plt.imsave(temp_image_path, image)

        video_filename = f"static/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        clip = ImageSequenceClip(images, fps=20)
        clip.write_videofile(video_filename, codec='libx264', audio=False)

        mri_images = [f"static/temp_image_{i}.png" for i in range(len(images))]

        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        create_medical_report(patient_info, prediagnosis, mri_images, report_filename)

        with open(video_filename, 'rb') as video_file:
            video_data = video_file.read()

        with open(report_filename, 'rb') as report_file:
            report_data = report_file.read()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO predictions (user_id, patient_id, patient_name, patient_age, patient_gender, prediagnosis, video, AI_BraTs_Function_report) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (user_id, patient_info['id'], patient_info['name'], patient_info['age'], patient_info['gender'],
             prediagnosis, psycopg2.Binary(video_data), psycopg2.Binary(report_data))
        )
        conn.commit()
        cursor.close()
        conn.close()

        delete_file_after_delay(video_filename, 600)
        os.remove(report_filename)
        video_url = f"{request.host_url}{video_filename}"
        return jsonify({"video_url": video_url})

    except Exception as e:
        print("Error durante la predicción:", str(e))
        return jsonify({"error": "Error durante la predicción. Consulta los registros del servidor para más detalles."}), 500
