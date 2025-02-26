
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

# Configuración del Blueprint para manejar rutas relacionadas con la predicción
predictionBratsAI = Blueprint('predictionBratsAI', __name__)

# Definición de parámetros del modelo
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 3
num_classes = 4

# Cargar modelo UNet 3D
try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('model_3D\\3 clases\\modelUnet3D_3.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

# Función para eliminar archivos después de un tiempo determinado
def delete_file_after_delay(file_path, delay):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")

    timer = threading.Timer(delay, delete_file)
    timer.start()
import psycopg2
from psycopg2.extras import RealDictCursor

# Conexión a la base de datos PostgreSQL
def get_db_connection():
    return psycopg2.connect(
<<<<<<< HEAD
        dbname='postgres',
        user='postgres.txfhmfkxzcwigxhzhvmx',
        password='VLNVddyd2002',
        host='aws-0-us-east-1.pooler.supabase.com',
        port='6543'
=======
        # dbname='postgres',
        # user='postgres.txfhmfkxzcwigxhzhvmx',
        # password='VLNVddyd2002',
        # host='aws-0-us-east-1.pooler.supabase.com',
        # port='6543'
        dbname='postgres',
        user='postgres',
        password='admin123',
        host='localhost',
        port='5432'
>>>>>>> diegotesis
    )

# Ruta para realizar la predicción
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

    # Conectar a la base de datos
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

        # Si ya existen las gráficas, devolver las URLs
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
        # Cargar imagen HDF5
        test_img = load_hdf5_file(h5_filename)
        if test_img is None:
            return jsonify({'message': 'Error al cargar el archivo HDF5.'}), 500

        # Realizar predicción con el modelo
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


# Ruta para generar la gráfica de diagnóstico 3D del paciente
@predictionBratsAI.route('/generate-graph6', methods=['POST'])
def generate_graph6_route():
    # Verificar si el usuario está autenticado, si no, devolver mensaje de error
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    # Verificar si se proporciona un patient_id en la solicitud
    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    # Construir la ruta del archivo HDF5 basado en el patient_id
    h5_filename = os.path.join('processed_files', f'{patient_id}.h5')

    # Verificar si el archivo HDF5 existe
    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

        # Cargar las imágenes desde el archivo HDF5
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


# Ruta para generar la gráfica de diagnóstico 3D del paciente
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


import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
import h5py

# Definición de funciones de métricas para evaluar la segmentación
def dice_coef(y_true, y_pred, smooth=1.0):
    y_true_f = tf.cast(K.flatten(y_true), dtype=tf.float32)
    y_pred_f = tf.cast(K.flatten(y_pred), dtype=tf.float32)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

def hausdorff_distance(y_true, y_pred):
    y_true = K.cast(y_true, 'float32')
    y_pred = K.cast(y_pred, 'float32')
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    return tf.reduce_max(tf.norm(y_true_f - y_pred_f, ord='euclidean'))

# Ruta para generar la gráfica de segmentación (con segmentación predicha y real)
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
        # Conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Cargar las imágenes y las segmentaciones desde el archivo HDF5
        with h5py.File(h5_filename, 'r') as hf:
            if 'images' not in hf or 'masks' not in hf:
                return jsonify({'message': 'El archivo HDF5 no contiene imágenes o segmentación.'}), 400

            test_img = hf['images'][:]
            real_segmentation = np.argmax(hf['masks'][:], axis=-1)  # Segmentación real en formato de clases

        # Verificar la forma de test_img antes de expand_dims
        print("Forma de test_img antes de expand_dims:", test_img.shape)
        test_img_input = np.expand_dims(test_img, axis=0) if len(test_img.shape) == 4 else test_img
        print("Forma de test_img después de expand_dims:", test_img_input.shape)

        # Obtener la segmentación predicha
        test_prediction = model.predict(test_img_input)
        predicted_segmentation = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # Cálculo de métricas de evaluación
        y_true = tf.convert_to_tensor(real_segmentation, dtype=tf.int32)
        y_pred = tf.convert_to_tensor(predicted_segmentation, dtype=tf.int32)

        dice_val = float(dice_coef(y_true, y_pred).numpy())
        mean_iou_metric = tf.keras.metrics.MeanIoU(num_classes=4)
        mean_iou_metric.update_state(y_true, y_pred)
        mean_iou_val = float(mean_iou_metric.result().numpy())
        hausdorff_val = float(hausdorff_distance(y_true, y_pred).numpy())

        # Informe sobre la Precisión General (similar al Coeficiente Dice)
        if dice_val < 0.5:
            dice_text = (
                f"El análisis muestra una *precisión baja* en la identificación de la zona afectada (valor: {dice_val:.2f}).\n"
                "Esto significa que la delimitación de la zona de interés en la imagen difiere considerablemente de la estructura real. "
                "Se sugiere revisar la calidad de la imagen o repetir el proceso para confirmar los hallazgos."
            )
        elif 0.5 <= dice_val < 0.8:
            dice_text = (
                f"El análisis indica una *precisión moderada* en la delimitación de la zona afectada (valor: {dice_val:.2f}).\n"
                "La segmentación es razonable, aunque se observan algunas discrepancias que podrían requerir una segunda verificación."
            )
        else:
            dice_text = (
                f"El análisis refleja una *alta precisión* en la delimitación de la zona afectada (valor: {dice_val:.2f}).\n"
                "La segmentación se ajusta muy bien a la estructura real, facilitando una interpretación confiable."
            )

        # Informe sobre el Grado de Superposición (similar al Índice IoU)
        if mean_iou_val < 0.5:
            iou_text = (
                f"El grado de superposición entre la imagen y la delimitación es *bajo* (valor: {mean_iou_val:.2f}).\n"
                "Esto indica que la correspondencia entre la zona segmentada y la real es limitada, lo que podría dificultar el diagnóstico."
            )
        elif 0.5 <= mean_iou_val < 0.8:
            iou_text = (
                f"El grado de superposición es *moderado* (valor: {mean_iou_val:.2f}).\n"
                "La correspondencia entre la imagen y la delimitación es aceptable, aunque se recomienda una revisión para asegurar la precisión en la interpretación clínica."
            )
        else:
            iou_text = (
                f"El grado de superposición es *alto* (valor: {mean_iou_val:.2f}).\n"
                "La imagen y la delimitación se corresponden muy bien, lo que respalda la confiabilidad del análisis."
            )

        # Informe sobre la Conformidad de la Forma (relacionado con la Distancia de Hausdorff)
        if hausdorff_val > 100:
            hausdorff_text = (
                f"Se detecta una *alta variabilidad* en la forma de la zona afectada (valor: {hausdorff_val:.2f}).\n"
                "Esto implica que existen diferencias notables entre la forma de la zona segmentada y la estructura real, lo que podría influir en la interpretación."
            )
        elif 50 < hausdorff_val <= 100:
            hausdorff_text = (
                f"Se observa una *variabilidad moderada* en la forma (valor: {hausdorff_val:.2f}).\n"
                "Aunque la segmentación es razonable, algunas discrepancias en la forma podrían necesitar una revisión adicional."
            )
        else:
            hausdorff_text = (
                f"La *variabilidad en la forma* es *baja* (valor: {hausdorff_val:.2f}).\n"
                "La forma de la zona afectada se corresponde de manera consistente con la estructura real, lo que favorece una evaluación clínica precisa."
            )

        # Informe final combinando los resultados
        medical_report = (
                f"{dice_text}\n\n"
                f"{iou_text}\n\n"
                f"{hausdorff_text}\n\n"
                "Conclusión:\n"
                "- Precisión en la delimitación de la zona afectada: " + (
                    "alta" if dice_val >= 0.8 else "moderada" if dice_val >= 0.5 else "baja"
                ) + ".\n"
                    "- Grado de superposición: " + (
                    "alto" if mean_iou_val >= 0.8 else "moderado" if mean_iou_val >= 0.5 else "bajo"
                ) + ".\n"
                    "- Conformidad en la forma: " + (
                    "alta" if hausdorff_val <= 50 else "moderada" if hausdorff_val <= 100 else "baja"
                ) + ".\n\n"
                    "Se recomienda considerar estos resultados en conjunto con la evaluación clínica del paciente. "

        )

        # Generar la gráfica con la segmentación real y predicha
        graphS_html = generate_graph_real_and_predicted_segmentation_with_brain(
            test_img, real_segmentation, predicted_segmentation
        )

        # Guardar la ruta de la gráfica en la base de datos
        cursor.execute("""
            UPDATE patients
            SET graph_segmentation_path = %s
            WHERE patient_id = %s
        """, (graphS_html, patient_id))

        conn.commit()
        conn.close()

        # Generar la URL para la gráfica
        graphS_url = url_for('static', filename=graphS_html, _external=True)

        # Retornar los resultados en formato JSON
        return jsonify({
            "htmlUrlS": graphS_url,
            "metrics": {
                "Dice Coefficient": dice_val,
                "Mean IoU": mean_iou_val,
                "Hausdorff Distance": hausdorff_val
            },
            "medical_report": medical_report
        })

    except Exception as e:
        # Manejar cualquier excepción y devolver mensaje de error
        print(f"Error al generar la gráfica 3-D: {str(e)}")
        return jsonify({"message": "Error al generar la gráfica. Consulta los registros del servidor para más detalles."}),500
