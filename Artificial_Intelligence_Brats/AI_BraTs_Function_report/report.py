import base64
import json
from flask import Flask, jsonify, request, render_template, send_file, url_for, make_response, session, Blueprint
from DataBase import create_tables, get_db_connection
from reports.reportePDF import PDF

report = Blueprint('AI_BraTs_Function_report', __name__)
def save_image(image_data, image_name):
    try:
        # Decodificar el string base64
        image_data = base64.b64decode(image_data.split(',')[1])
        file_path = f'static/images/{image_name}.png'
        with open(file_path, 'wb') as f:
            f.write(image_data)
        return file_path
    except Exception as e:
        print(f"Error al guardar la imagen {image_name}: {e}")
        return None
@report.route('/send-report', methods=['POST'])
def send_report():
    data = request.json
    patient_id = data.get('patient_id')
    report_text2 = data.get('report_text2')
    report_text5 = data.get('report_text5')
    graph2_image = data.get('graph2_image')
    graph5_image = data.get('graph5_image')
    feedback = data.get('feedback')
    modalities_description = data.get('modalities_description')
    user_id = session.get('user_id')

    # Codifica las cadenas en UTF-8
    report_text2_utf8 = report_text2.encode('utf-8').decode('utf-8')
    report_text5_utf8 = report_text5.encode('utf-8').decode('utf-8')
    feedback_utf8 = {key: value.encode('utf-8').decode('utf-8') for key, value in feedback.items()}
    modalities_description_utf8 = modalities_description.encode('utf-8').decode('utf-8')

    # Descripción de las modalidades
    modalities_description_text = """
        1. T1c (T1-weighted contrast-enhanced imaging): Esta modalidad se utiliza para resaltar estructuras anatómicas y anormalidades en el cerebro. La administración de un agente de contraste mejora la visualización de lesiones como tumores, inflamaciones y áreas de ruptura de la barrera hematoencefálica.

        2. T2w (T2-weighted imaging): Esta modalidad se utiliza para resaltar diferencias en el contenido de agua de los tejidos cerebrales. Es útil para identificar lesiones que contienen líquido, como edemas, inflamaciones y algunos tipos de tumores.

        3. FLAIR (Fluid-Attenuated Inversion Recovery): Esta modalidad es una variación de la imagen ponderada en T2 que suprime el líquido cefalorraquídeo, permitiendo una mejor visualización de lesiones cerca de los ventrículos cerebrales y otras áreas de alto contenido de agua.
        """
    # Verificar que todos los datos estén presentes
    if not all([patient_id, report_text2, report_text5, graph2_image, graph5_image, feedback, modalities_description, user_id]):
        return jsonify({"error": "Faltan datos en la solicitud"}), 400

    graph2_image_path = save_image(graph2_image, 'graph2')
    graph5_image_path = save_image(graph5_image, 'graph5')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (user_id, patient_id, report_text2, report_text5, graph2_image_path, graph5_image_path, feedback, modalities_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, patient_id, report_text2_utf8, report_text5_utf8, graph2_image_path, graph5_image_path, json.dumps(feedback_utf8), modalities_description_utf8))
        conn.commit()
        cursor.close()
        conn.close()

        # Generar el PDF
        pdf = PDF()
        pdf.add_page()

        # Encabezado del Reporte
        pdf.add_patient_info(patient_id)

        # Descripción de Modalidades
        pdf.add_modalities_description()

        # Reporte de Textura
        pdf.chapter_title('Reporte de Textura')
        pdf.chapter_body(report_text2)

        # Reporte de Predicción
        pdf.chapter_title('Reporte de Predicción')
        pdf.chapter_body(report_text5)

        # Feedback
        pdf.chapter_title('Feedback')
        formatted_feedback = pdf.format_feedback(feedback)
        pdf.chapter_body(formatted_feedback)

        # Crear un archivo temporal para el PDF
        temp_pdf_path = f'reporte_paciente_{patient_id}.pdf'
        pdf.output(temp_pdf_path)

        return send_file(temp_pdf_path, as_attachment=True, download_name='reporte_paciente.pdf',
                         mimetype='application/pdf')

    except Exception as e:
        print(f"Error al guardar el reporte: {e}")
        return jsonify({"error": "Error al guardar el reporte"}), 500

@report.route('/download-report/<patient_id>', methods=['GET'])
def download_report(patient_id):
    try:
        temp_pdf_path = f'reporte_paciente_{patient_id}.pdf'
        return send_file(temp_pdf_path, as_attachment=True, download_name=f'reporte_paciente_{patient_id}.pdf', mimetype='application/pdf')
    except Exception as e:
        print(f"Error al descargar el reporte: {e}")
        return jsonify({"error": "Error al descargar el reporte"}), 500
