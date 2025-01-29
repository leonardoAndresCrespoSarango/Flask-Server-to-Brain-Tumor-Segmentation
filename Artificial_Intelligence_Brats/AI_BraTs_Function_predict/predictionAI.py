
import os
import threading

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
import psycopg2
from psycopg2.extras import RealDictCursor

# Función para obtener conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        dbname='postgres',
        user='postgres.txfhmfkxzcwigxhzhvmx',
        password='VLNVddyd2002',
        host='aws-0-us-east-1.pooler.supabase.com',
        port='6543'
    )

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
        # Verificar si ya existen las gráficas en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT graph1_path, graph2_path, graph3_path, graph4_path, graph5_path, graph6_path
            FROM patients
            WHERE patient_id = %s
        """, (patient_id,))

        result = cursor.fetchone()

        if result and all(result.values()):
            # Si ya existen las gráficas, devolver las rutas almacenadas
            conn.close()
            return jsonify({
                "html_url1": url_for('static', filename=result['graph1_path'], _external=True),
                "html_url2": url_for('static', filename=result['graph2_path'], _external=True),
                "html_url3": url_for('static', filename=result['graph3_path'], _external=True),
                "html_url4": url_for('static', filename=result['graph4_path'], _external=True),
                "html_url5": url_for('static', filename=result['graph5_path'], _external=True),
                "html_url6": url_for('static', filename=result['graph6_path'], _external=True)
            })

        # Si no existen las gráficas, generarlas
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

        # Guardar las rutas en la base de datos
        cursor.execute("""
            UPDATE patients
            SET graph1_path = %s, graph2_path = %s, graph3_path = %s,
                graph4_path = %s, graph5_path = %s, graph6_path = %s
            WHERE patient_id = %s
        """, (graph1_html, graph2_html, graph3_html,
              graph4_html, graph5_html, graph6_html, patient_id))

        conn.commit()
        conn.close()

        return jsonify({
            "html_url1": url_for('static', filename=graph1_html, _external=True),
            "html_url2": url_for('static', filename=graph2_html, _external=True),
            "html_url3": url_for('static', filename=graph3_html, _external=True),
            "html_url4": url_for('static', filename=graph4_html, _external=True),
            "html_url5": url_for('static', filename=graph5_html, _external=True),
            "html_url6": url_for('static', filename=graph6_html, _external=True),
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


@predictionBratsAI.route('/generate-graphDiagnostic', methods=['POST'])
def graphDiagnostic_route():
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
        graph6_html = generate_graphDiagnostic(test_img)

        # Generar la URL para la gráfica
        graph6_url = url_for('static', filename=graph6_html, _external=True)

        return jsonify({
            "htmlUrl3D": graph6_url
        })

    except Exception as e:
        print(f"Error al generar la gráfica 3D: {str(e)}")
        return jsonify({"message": "Error al generar la gráfica 6. Consulta los registros del servidor para más detalles."}), 500


import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
import h5py
from flask import jsonify, request, url_for, session

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
import h5py
from flask import jsonify, request, url_for, session

@predictionBratsAI.route('/generate-graphSegmentation', methods=['POST'])
def graphSegmentation_route():
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    h5_filename = os.path.join('processed_files', f'{patient_id}_withSeg.h5')

    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

    try:
        # Cargar las imágenes y segmentaciones desde el archivo HDF5
        with h5py.File(h5_filename, 'r') as hf:
            if 'images' not in hf or 'masks' not in hf:
                return jsonify({'message': 'El archivo HDF5 no contiene imágenes o segmentación.'}), 400

            test_img = hf['images'][:]
            real_segmentation = np.argmax(hf['masks'][:], axis=-1)  # Segmentación real (clases)

        # Obtener la segmentación predicha
        test_img_input = np.expand_dims(test_img[..., :4], axis=0)  # Si necesitas 4 canales
        test_prediction = model.predict(test_img_input)
        predicted_segmentation = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # 🔹 **Cálculo de métricas**
        def dice_coef(y_true, y_pred, smooth=1.0):
            y_true_f = tf.cast(K.flatten(y_true), dtype=tf.float32)
            y_pred_f = tf.cast(K.flatten(y_pred), dtype=tf.float32)
            intersection = K.sum(y_true_f * y_pred_f)
            return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

        def hausdorff_distance(y_true, y_pred):
            y_true_f = K.cast(K.flatten(y_true), dtype=tf.float32)  # Convertir a float32
            y_pred_f = K.cast(K.flatten(y_pred), dtype=tf.float32)  # Convertir a float32
            return tf.reduce_max(tf.norm(y_true_f - y_pred_f, ord='euclidean'))

        # Convertir segmentaciones a tensores
        y_true = tf.convert_to_tensor(real_segmentation, dtype=tf.int32)
        y_pred = tf.convert_to_tensor(predicted_segmentation, dtype=tf.int32)

        # Cálculo de métricas
        dice_val = dice_coef(y_true, y_pred).numpy()
        mean_iou_metric = tf.keras.metrics.MeanIoU(num_classes=4)
        mean_iou_metric.update_state(y_true, y_pred)
        mean_iou_val = mean_iou_metric.result().numpy()
        hausdorff_val = hausdorff_distance(y_true, y_pred).numpy()

        # 🔹 **Generar texto descriptivo**
        def generate_medical_report(dice, iou, hausdorff):
            report = "🔍 **Informe de Segmentación Tumoral** 🔍\n\n"

            # Evaluación Dice Coefficient
            if dice > 0.85:
                report += "✅ La segmentación muestra una **alta concordancia** con la segmentación real.\n"
            elif dice > 0.70:
                report += "⚠️ La segmentación tiene una **buena precisión**, pero puede mejorarse.\n"
            else:
                report += "❌ La segmentación tiene **baja precisión**, lo que puede indicar errores en el modelo.\n"

            # Evaluación Mean IoU
            if iou > 0.75:
                report += "✅ El índice de superposición (IoU) indica una **buena identificación de las regiones tumorales**.\n"
            elif iou > 0.50:
                report += "⚠️ La segmentación tiene una **cobertura moderada**, puede haber regiones mal clasificadas.\n"
            else:
                report += "❌ La segmentación presenta **poca coincidencia con la referencia**, revisar la predicción.\n"

            # Evaluación Hausdorff Distance
            if hausdorff < 10:
                report += "✅ La distancia Hausdorff indica una **buena alineación** con la segmentación real.\n"
            elif hausdorff < 50:
                report += "⚠️ Existen algunas diferencias significativas entre la predicción y la segmentación real.\n"
            else:
                report += "❌ Alta distancia Hausdorff, lo que sugiere **errores en la segmentación** y posibles bordes irregulares.\n"

            report += "\n📌 **Conclusión:** Los resultados de segmentación deben interpretarse en el contexto clínico del paciente y, en caso de discrepancia, se recomienda una evaluación manual por parte del especialista."
            return report

        # Generar el informe médico
        medical_report = generate_medical_report(dice_val, mean_iou_val, hausdorff_val)

        # 🔹 **Salida de métricas y diagnóstico**
        print(f"📊 Dice Coefficient: {dice_val:.4f}")
        print(f"📊 Mean IoU: {mean_iou_val:.4f}")
        print(f"📊 Hausdorff Distance: {hausdorff_val:.4f}")
        print(f"📜 Informe médico: {medical_report}")

        # Generar la gráfica con segmentaciones
        graphS_html = generate_graph_real_and_predicted_segmentation_with_brain(
            test_img, real_segmentation, predicted_segmentation
        )

        # Generar la URL para la gráfica
        graphS_url = url_for('static', filename=graphS_html, _external=True)

        return jsonify({
            "htmlUrlS": graphS_url,
            "metrics": {
                "Dice Coefficient": float(dice_val),
                "Mean IoU": float(mean_iou_val),
                "Hausdorff Distance": float(hausdorff_val)
            },
            "medical_report": medical_report  # Se envía el informe como texto
        })

    except Exception as e:
        print(f"❌ Error al generar la gráfica y métricas: {str(e)}")
        return jsonify({"message": "Error al generar la gráfica y métricas. Consulta los registros del servidor para más detalles."}), 500
