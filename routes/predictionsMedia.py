from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection

# Creación de un Blueprint para organizar las rutas de predicciones
prediction = Blueprint('prediction', __name__)

# Ruta para obtener el video asociado a una predicción
@prediction.route('/predictions/<int:prediction_id>/video', methods=['GET'])
def get_prediction_video(prediction_id):
    # Verificamos si el usuario está autenticado (si su ID está en la sesión)
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        # Conexión a la base de datos para obtener el video asociado a la predicción
        conn = get_db_connection()
        cursor = conn.cursor()
        # Realizamos la consulta para obtener el video de la predicción del usuario autenticado
        cursor.execute('SELECT video FROM predictions WHERE id = %s AND user_id = %s', (prediction_id, session['user_id']))
        video_data = cursor.fetchone()
        cursor.close()
        conn.close()

        # Verificamos si no se encontró el video
        if video_data is None:
            return jsonify({"error": "Video no encontrado"}), 404
        # Preparación de la respuesta con los datos del video
        response = make_response(bytes(video_data[0]))
        response.headers.set('Content-Type', 'video/mp4')
        response.headers.set('Content-Disposition', 'attachment', filename=f'video_{prediction_id}.mp4')
        return response

    except Exception as e:
        # Si ocurre un error durante la consulta, retornamos un mensaje de error
        print("Error al recuperar el video:", str(e))
        return jsonify({"error": "Error al recuperar el video. Consulta los registros del servidor para más detalles."}), 500


# Ruta para obtener el reporte asociado a una predicción
@prediction.route('/predictions/<int:prediction_id>/report', methods=['GET'])
def get_prediction_report(prediction_id):
    # Verificamos si el usuario está autenticado (si su ID está en la sesión)
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        # Conexión a la base de datos para obtener el reporte asociado a la predicción
        conn = get_db_connection()
        cursor = conn.cursor()
        # Realizamos la consulta para obtener el reporte de la predicción del usuario autenticado
        cursor.execute('SELECT AI_BraTs_Function_report FROM predictions WHERE id = %s AND user_id = %s', (prediction_id, session['user_id']))
        report_data = cursor.fetchone()
        cursor.close()
        conn.close()
        # Verificamos si no se encontró el reporte
        if report_data is None:
            return jsonify({"error": "Reporte no encontrado"}), 404

        # Preparación de la respuesta con los datos del reporte
        response = make_response(bytes(report_data[0]))
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename=f'report_{prediction_id}.pdf')
        return response

    except Exception as e:
        print("Error al recuperar el reporte:", str(e))
        return jsonify({"error": "Error al recuperar el reporte. Consulta los registros del servidor para más detalles."}), 500