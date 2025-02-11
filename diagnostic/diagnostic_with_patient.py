from flask import Flask, jsonify, session, Blueprint
from DataBase import get_db_connection
from psycopg2.extras import RealDictCursor

#Blueprint para el acceso al diagnóstico del paciente
diagnostic_patient = Blueprint('diagnostic_patient', __name__)
@diagnostic_patient.route('/patients-with-diagnostics', methods=['GET'])
def get_patients_with_diagnostics():
    # Verificar si el usuario está autenticado
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Consulta SQL para obtener pacientes con sus diagnósticos
        # Se utiliza LEFT JOIN para incluir pacientes sin diagnóstico
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
        # Recuperar los resultados de la consulta
        patients = cursor.fetchall()
        # Cerrar la conexión con la base de datos
        cursor.close()
        conn.close()
        # Devolver los resultados como respuesta en formato JSON
        return jsonify(patients)

    except Exception as e:
        # En caso de error, capturar la excepción y devolver un mensaje de error
        print("Error al recuperar los pacientes:", str(e))
        return jsonify(
            {"error": "Error al recuperar los pacientes. Consulta los registros del servidor para más detalles."}), 500

