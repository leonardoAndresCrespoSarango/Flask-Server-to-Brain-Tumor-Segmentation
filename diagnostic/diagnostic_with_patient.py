from flask import Flask, jsonify, session, Blueprint
from DataBase import get_db_connection
from psycopg2.extras import RealDictCursor
diagnostic_patient = Blueprint('diagnostic_patient', __name__)
@diagnostic_patient.route('/patients-with-diagnostics', methods=['GET'])
def get_patients_with_diagnostics():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Actualiza la consulta para incluir is_generated
        cursor.execute("""
                SELECT 
                    p.patient_id, 
                    p.numero_historia_clinica,
                    COALESCE(d.is_generated, FALSE) AS is_generated
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
        return jsonify(
            {"error": "Error al recuperar los pacientes. Consulta los registros del servidor para más detalles."}), 500

