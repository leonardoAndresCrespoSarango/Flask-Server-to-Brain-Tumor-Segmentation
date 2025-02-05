import base64
import json
from flask import Flask, jsonify, request, render_template, send_file, url_for, make_response, session, Blueprint
from DataBase import create_tables, get_db_connection
from reports.reportePDF import PDF

# Blueprint que maneja las rutas y funciones relacionadas con la generación de reportes
report = Blueprint('AI_BraTs_Function_report', __name__)

# Función para guardar imágenes codificadas en base64 como archivos PNG
def save_image(image_data, image_name):
    try:
        # Decodificar el string base64
        image_data = base64.b64decode(image_data.split(',')[1])

        # Definir la ruta de almacenamiento de la imagen
        file_path = f'static/images/{image_name}.png'

        # Guardar la imagen en el disco
        with open(file_path, 'wb') as f:
            f.write(image_data)
        return file_path
    except Exception as e:

        # Manejo de errores si algo sale mal al guardar la imagen
        print(f"Error al guardar la imagen {image_name}: {e}")
        return None

# Ruta para recibir el reporte y generar el PDF
@report.route('/send-report', methods=['POST'])
def send_report():
    # Recibir los datos enviados en la solicitud POST
    data = request.json
    patient_id = data.get('patient_id')
    report_text2 = data.get('report_text2')
    report_text5 = data.get('report_text5')
    graph2_image = data.get('graph2_image')
    graph5_image = data.get('graph5_image')
    feedback = data.get('feedback')
    modalities_description = data.get('modalities_description')
    user_id = session.get('user_id')

    # Codificar las cadenas en UTF-8 para evitar problemas de caracteres
    report_text2_utf8 = report_text2.encode('utf-8').decode('utf-8')
    report_text5_utf8 = report_text5.encode('utf-8').decode('utf-8')
    feedback_utf8 = {key: value.encode('utf-8').decode('utf-8') for key, value in feedback.items()}
    modalities_description_utf8 = modalities_description.encode('utf-8').decode('utf-8')

    # Descripción de las modalidades de imagen utilizadas en el reporte
    modalities_description_text = """
        1. T1c (T1-weighted contrast-enhanced imaging): Esta modalidad se utiliza para resaltar estructuras anatómicas y anormalidades en el cerebro. La administración de un agente de contraste mejora la visualización de lesiones como tumores, inflamaciones y áreas de ruptura de la barrera hematoencefálica.

        2. T2w (T2-weighted imaging): Esta modalidad se utiliza para resaltar diferencias en el contenido de agua de los tejidos cerebrales. Es útil para identificar lesiones que contienen líquido, como edemas, inflamaciones y algunos tipos de tumores.

        3. FLAIR (Fluid-Attenuated Inversion Recovery): Esta modalidad es una variación de la imagen ponderada en T2 que suprime el líquido cefalorraquídeo, permitiendo una mejor visualización de lesiones cerca de los ventrículos cerebrales y otras áreas de alto contenido de agua.
        """
    # Verificar que todos los datos necesarios estén presentes
    if not all([patient_id, report_text2, report_text5, graph2_image, graph5_image, feedback, modalities_description, user_id]):
        return jsonify({"error": "Faltan datos en la solicitud"}), 400

    # Guardar las imágenes codificadas en base64
    graph2_image_path = save_image(graph2_image, 'graph2')
    graph5_image_path = save_image(graph5_image, 'graph5')

    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar el reporte y los datos en la base de datos
        cursor.execute("""
            INSERT INTO reports (user_id, patient_id, report_text2, report_text5, graph2_image_path, graph5_image_path, feedback, modalities_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, patient_id, report_text2_utf8, report_text5_utf8, graph2_image_path, graph5_image_path, json.dumps(feedback_utf8), modalities_description_utf8))

        # Confirmar los cambios en la base de datos
        conn.commit()
        cursor.close()
        conn.close()

        # Crear un objeto PDF para generar el reporte
        pdf = PDF()
        pdf.add_page()

        # Agregar información del paciente al reporte
        pdf.add_patient_info(patient_id)

        # Agregar la descripción de las modalidades de imagen al reporte
        pdf.add_modalities_description()

        # Agregar el reporte de textura al PDF
        pdf.chapter_title('Reporte de Textura')
        pdf.chapter_body(report_text2)

        # Agregar el reporte de predicción al PDF
        pdf.chapter_title('Reporte de Predicción')
        pdf.chapter_body(report_text5)

        # Agregar el feedback al PDF
        pdf.chapter_title('Feedback')
        formatted_feedback = pdf.format_feedback(feedback)
        pdf.chapter_body(formatted_feedback)

        # Crear un archivo temporal para el PDF
        temp_pdf_path = f'reporte_paciente_{patient_id}.pdf'
        pdf.output(temp_pdf_path)

        # Enviar el archivo PDF generado como respuesta para su descarga
        return send_file(temp_pdf_path, as_attachment=True, download_name='reporte_paciente.pdf',
                         mimetype='application/pdf')

    except Exception as e:
        # Manejo de errores si ocurre un problema durante la generación o guardado del reporte
        print(f"Error al guardar el reporte: {e}")
        return jsonify({"error": "Error al guardar el reporte"}), 500


# Ruta para descargar un reporte específico por ID de paciente
@report.route('/download-report/<patient_id>', methods=['GET'])
def download_report(patient_id):
    try:
        temp_pdf_path = f'reporte_paciente_{patient_id}.pdf'
        return send_file(temp_pdf_path, as_attachment=True, download_name=f'reporte_paciente_{patient_id}.pdf', mimetype='application/pdf')
    except Exception as e:
        print(f"Error al descargar el reporte: {e}")
        return jsonify({"error": "Error al descargar el reporte"}), 500
