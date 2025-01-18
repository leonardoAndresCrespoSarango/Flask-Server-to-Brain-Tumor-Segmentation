from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
prediction = Blueprint('prediction', __name__)
@prediction.route('/predictions/<int:prediction_id>/video', methods=['GET'])
def get_prediction_video(prediction_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT video FROM predictions WHERE id = %s AND user_id = %s', (prediction_id, session['user_id']))
        video_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if video_data is None:
            return jsonify({"error": "Video no encontrado"}), 404

        response = make_response(bytes(video_data[0]))
        response.headers.set('Content-Type', 'video/mp4')
        response.headers.set('Content-Disposition', 'attachment', filename=f'video_{prediction_id}.mp4')
        return response

    except Exception as e:
        print("Error al recuperar el video:", str(e))
        return jsonify({"error": "Error al recuperar el video. Consulta los registros del servidor para más detalles."}), 500

@prediction.route('/predictions/<int:prediction_id>/report', methods=['GET'])
def get_prediction_report(prediction_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT AI_BraTs_Function_report FROM predictions WHERE id = %s AND user_id = %s', (prediction_id, session['user_id']))
        report_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if report_data is None:
            return jsonify({"error": "Reporte no encontrado"}), 404

        response = make_response(bytes(report_data[0]))
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename=f'report_{prediction_id}.pdf')
        return response

    except Exception as e:
        print("Error al recuperar el reporte:", str(e))
        return jsonify({"error": "Error al recuperar el reporte. Consulta los registros del servidor para más detalles."}), 500