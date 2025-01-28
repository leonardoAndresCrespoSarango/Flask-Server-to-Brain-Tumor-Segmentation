
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
        'numero_historia_clinica': data.get('numeroHistoriaClinica'),
        'survey_completed': False  # Inicializamos como False
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO patients (user_id, patient_id, numero_historia_clinica, survey_completed) VALUES (%s, %s, %s, %s)',
            (user_id, patient_info['id'], patient_info['numero_historia_clinica'], patient_info['survey_completed'])
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
        cursor.execute("""
                   SELECT 
                       p.patient_id, 
                       p.numero_historia_clinica,
                       p.survey_completed,
                       d.is_generated,
                       d.cancer_status,
                       d.report_path
                   FROM patients p
                   LEFT JOIN diagnostics d 
                   ON p.patient_id = d.patient_id
                   WHERE p.user_id = %s
               """, (user_id,))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(patients)

    except Exception as e:
        print("Error al recuperar los pacientes:", str(e))
        return jsonify({"error": "Error al recuperar los pacientes. Consulta los registros del servidor para más detalles."}), 500


@patient.route('/patients/<patient_id>/survey-status', methods=['PUT'])
def update_survey_status(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    # Obtener el estado de la encuesta desde el cuerpo de la solicitud
    data = request.get_json()  # Obtén el cuerpo JSON
    survey_completed = data.get('survey_completed', None)

    if survey_completed is None:
        return jsonify({"error": "Estado de la encuesta no proporcionado"}), 400

    # Verificar que survey_completed sea un booleano
    if not isinstance(survey_completed, bool):
        return jsonify({"error": "El valor de 'survey_completed' debe ser un valor booleano (true o false)."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el paciente existe para el usuario
        cursor.execute(
            'SELECT 1 FROM patients WHERE patient_id = %s AND user_id = %s',
            (patient_id, user_id)
        )
        if cursor.fetchone() is None:
            return jsonify(
                {"error": "No se encontró el paciente o no tienes permisos para actualizar este estado."}), 404

        # Si el paciente existe, actualizamos el estado de la encuesta
        cursor.execute(
            'UPDATE patients SET survey_completed = %s WHERE patient_id = %s AND user_id = %s',
            (survey_completed, patient_id, user_id)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "No se pudo actualizar el estado de la encuesta."}), 500

        conn.commit()

        return jsonify({'message': 'Estado de encuesta actualizado exitosamente'}), 200

    except Exception as e:
        patient.logger.error(f"Error al actualizar el estado de la encuesta: {str(e)}")
        return jsonify({
                           "error": "Error al actualizar el estado de la encuesta. Consulta los registros del servidor para más detalles."}), 500

    finally:
        # Asegúrate de cerrar la conexión y el cursor independientemente de que haya error o no
        if conn:
            conn.close()
        if cursor:
            cursor.close()
