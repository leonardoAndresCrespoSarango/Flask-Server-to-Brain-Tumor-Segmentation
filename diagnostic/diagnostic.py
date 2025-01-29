from datetime import datetime

import pytz
from flask import jsonify, request, session, \
    Blueprint, send_from_directory

from DataBase import get_db_connection
from psycopg2.extras import RealDictCursor

from reportes.reporte import generate_medical_report

diagnostic = Blueprint('diagnostic', __name__)

# Ruta para obtener diagnósticos de un paciente
@diagnostic.route('/add-diagnostic', methods=['POST'])
def add_diagnostic():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    data = request.json

    diagnostic_info = {
        'patient_id': data.get('patient_id'),
        'cancer_status': data.get('cancer_status'),  # Ahora es un texto del ENUM
        'description': data.get('description')
    }

    if diagnostic_info['cancer_status'] not in ['cancer detectado', 'no se detecta cancer', 'diagnostico incierto']:
        return jsonify({"error": "Valor inválido para cancer_status"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si ya existe un diagnóstico generado para el paciente
        cursor.execute(
            '''
            SELECT id, report_path, created_at, updated_at FROM diagnostics 
            WHERE patient_id = %s AND is_generated = TRUE
            ''',
            (diagnostic_info['patient_id'],)
        )
        existing_diagnostic = cursor.fetchone()

        if existing_diagnostic:
            # Actualizar el diagnóstico existente
            diagnostic_id = existing_diagnostic[0]
            created_at = existing_diagnostic[2]
            updated_at = datetime.now(pytz.timezone('America/Guayaquil'))  # Hora actual ajustada a Ecuador

            cursor.execute(
                '''
               UPDATE diagnostics 
                SET cancer_status = %s, description = %s, user_id = %s, updated_at = %s 
                WHERE id = %s
                ''',
                (
                    diagnostic_info['cancer_status'],
                    diagnostic_info['description'],
                    user_id,
                    updated_at,
                    diagnostic_id
                )
            )
            conn.commit()
            message = 'Diagnóstico actualizado exitosamente'
        else:
            # Insertar un nuevo diagnóstico
            cursor.execute(
                '''
                INSERT INTO diagnostics (patient_id, user_id, cancer_status, description, is_generated) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id, created_at
                ''',
                (
                    diagnostic_info['patient_id'],
                    user_id,
                    diagnostic_info['cancer_status'],
                    diagnostic_info['description'],
                    True
                )
            )
            result = cursor.fetchone()
            diagnostic_id = result[0]
            created_at = result[1]
            updated_at = None  # No hay actualización en un diagnóstico recién creado
            conn.commit()
            message = 'Diagnóstico agregado exitosamente'

        # Obtener información adicional del usuario y del paciente
        cursor.execute('SELECT nombre, username FROM users WHERE id = %s', (user_id,))
        user_info = cursor.fetchone()

        cursor.execute(
            'SELECT numero_historia_clinica FROM patients WHERE patient_id = %s',
            (diagnostic_info['patient_id'],)
        )
        patient_info = cursor.fetchone()

        # Generar el reporte en LaTeX
        report_path = generate_medical_report(
            patient_id=diagnostic_info['patient_id'],
            patient_history=patient_info[0],
            cancer_status = diagnostic_info['cancer_status'],
            description=diagnostic_info['description'],
            doctor_name=user_info[0],
            doctor_username=user_info[1],
            created_at=created_at.astimezone(pytz.timezone('America/Guayaquil')),
            updated_at=updated_at
        )

        # Actualizar la tabla `diagnostics` con la ruta del reporte
        cursor.execute(
            '''
            UPDATE diagnostics SET report_path = %s WHERE id = %s
            ''',
            (report_path, diagnostic_id)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'message': message + ' y reporte generado',
            'report_path': report_path,
            'created_at': created_at
        })

    except Exception as e:
        print("Error al agregar o actualizar el diagnóstico:", str(e))
        return jsonify(
            {"error": "Error al agregar o actualizar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500


@diagnostic.route('/diagnostics/<patient_id>', methods=['GET'])
def get_diagnostics(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Recuperar el campo booleano `has_cancer` en lugar de `title`
        cursor.execute('SELECT id, cancer_status, description, created_at FROM diagnostics WHERE patient_id = %s AND user_id = %s', (patient_id, user_id))
        diagnostics = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(diagnostics)

    except Exception as e:
        print("Error al recuperar los diagnósticos:", str(e))
        return jsonify({"error": "Error al recuperar los diagnósticos. Consulta los registros del servidor para más detalles."}), 500


@diagnostic.route('/update-diagnostic', methods=['POST'])
def update_diagnostic():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.json
    patient_id = data.get('patient_id')
    has_cancer = data.get('has_cancer')  # Espera un booleano
    description = data.get('description')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Actualizar el diagnóstico con el campo `has_cancer`
        cursor.execute('UPDATE diagnostics SET cancer_status = %s, description = %s WHERE patient_id = %s AND user_id = %s',
                       (has_cancer, description, patient_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Diagnóstico actualizado exitosamente'})

    except Exception as e:
        print("Error al actualizar el diagnóstico:", str(e))
        return jsonify({"error": "Error al actualizar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500


@diagnostic.route('/get-diagnostic/<patient_id>', methods=['GET'])
def get_diagnostic(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Recuperar el campo `has_cancer` en lugar de `title`
        cursor.execute('SELECT cancer_status, description, is_generated FROM diagnostics WHERE patient_id = %s AND user_id = %s',
                       (patient_id, session['user_id']))
        diagnostic = cursor.fetchone()
        cursor.close()
        conn.close()

        if diagnostic:
            return jsonify(diagnostic)
        else:
            return jsonify({"error": "Diagnóstico no encontrado"}), 404

    except Exception as e:
        print("Error al recuperar el diagnóstico:", str(e))
        return jsonify({"error": "Error al recuperar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500

@diagnostic.route('/reportes/<path:filename>')
def serve_report(filename):
    return send_from_directory('reportes', filename)
