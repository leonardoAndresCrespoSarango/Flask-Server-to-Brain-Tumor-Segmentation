from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
from psycopg2.extras import RealDictCursor

patient = Blueprint('patient', __name__)
@patient.route('/add-patient', methods=['POST'])
def add_patient():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    data = request.json

    patient_info = {
        'id': data.get('patientId'),
        'numero_historia_clinica': data.get('numeroHistoriaClinica')
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO patients (user_id, patient_id, numero_historia_clinica) VALUES (%s, %s, %s)',
            (user_id, patient_info['id'], patient_info['numero_historia_clinica'])
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Paciente agregado exitosamente'})

    except Exception as e:
        print("Error al agregar el paciente:", str(e))
        return jsonify({"error": "Error al agregar el paciente. Consulta los registros del servidor para más detalles."}), 500

@patient.route('/patients', methods=['GET'])
def get_patients():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT patient_id, numero_historia_clinica FROM patients WHERE user_id = %s', (user_id,))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(patients)

    except Exception as e:
        print("Error al recuperar los pacientes:", str(e))
        return jsonify({"error": "Error al recuperar los pacientes. Consulta los registros del servidor para más detalles."}), 500

