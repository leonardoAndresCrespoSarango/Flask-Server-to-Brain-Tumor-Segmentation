import base64
import json
import threading
import os
from pylatex import Document, Section, Tabular, Command, Figure, Package, Subsection
from pylatex.utils import NoEscape, bold
import subprocess
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
import sys
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from skimage.transform import resize
import h5py
import glob
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import nibabel as nib
import matplotlib.pyplot as plt

from DataBase import create_tables, get_db_connection
from UNET import UNet
from H5 import load_hdf5_file
from moviepy.editor import ImageSequenceClip
import psycopg2
from psycopg2.extras import RealDictCursor
from graficas.graficasPloty import generate_graph1, generate_graph2, generate_graph3, generate_graph4, generate_graph5, \
    generate_graph6, generate_graph6_no_prediction
from latex.plantilla import create_medical_report
import bcrypt
import smtplib
from email.mime.text import MIMEText
from reports.reportePDF import PDF
from routes import routes, login, prediction, user
from routes.routes import send_reset_email
diagnostic = Blueprint('diagnostic', __name__)

@diagnostic.route('/add-diagnostic', methods=['POST'])
def add_diagnostic():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    data = request.json

    diagnostic_info = {
        'patient_id': data.get('patient_id'),
        'title': data.get('title'),
        'description': data.get('description')
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insertar el diagnóstico con `is_generated` como True
        cursor.execute(
            'INSERT INTO diagnostics (patient_id, user_id, title, description, is_generated) VALUES (%s, %s, %s, %s, %s)',
            (diagnostic_info['patient_id'], user_id, diagnostic_info['title'], diagnostic_info['description'], True)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Diagnóstico agregado exitosamente y marcado como generado'})

    except Exception as e:
        print("Error al agregar el diagnóstico:", str(e))
        return jsonify({"error": "Error al agregar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500

# Ruta para obtener diagnósticos de un paciente
@diagnostic.route('/diagnostics/<patient_id>', methods=['GET'])
def get_diagnostics(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, title, description, created_at FROM diagnostics WHERE patient_id = %s AND user_id = %s', (patient_id, user_id))
        diagnostics = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(diagnostics)

    except Exception as e:
        print("Error al recuperar los diagnósticos:", str(e))
        return jsonify({"error": "Error al recuperar los diagnósticos. Consulta los registros del servidor para más detalles."}), 500

@diagnostic.route('/generate-diagnostic-pdf', methods=['POST'])
def generate_diagnostic_pdf():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    data = request.json

    diagnostic_info = {
        'patient_id': data.get('patient_id'),
        'title': data.get('title'),
        'description': data.get('description')
    }

    patient_info = {
        'name': data.get('patient_name'),
        'age': data.get('patient_age'),
        'gender': data.get('patient_gender')
    }

    try:
        pdf_filename = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        create_diagnostic_pdf(patient_info, diagnostic_info, pdf_filename)

        pdf_url = url_for('static', filename=pdf_filename, _external=True)
        return jsonify({'pdf_url': pdf_url})

    except Exception as e:
        print("Error al generar el PDF del diagnóstico:", str(e))
        return jsonify({"error": "Error al generar el PDF del diagnóstico. Consulta los registros del servidor para más detalles."}), 500


def create_diagnostic_pdf(patient_info, diagnostic_info, pdf_filename):
    doc = Document(documentclass='article', document_options=['12pt', 'a4paper'])

    doc.preamble.append(Command('title', 'Diagnóstico Imagenológico'))
    doc.preamble.append(Command('author', 'Hospital XYZ'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\newpage'))

    with doc.create(Section('Información del Paciente')):
        with doc.create(Tabular('ll')) as table:
            table.add_row((bold('Nombre:'), patient_info['name']))
            table.add_row((bold('Edad:'), patient_info['age']))
            table.add_row((bold('Género:'), patient_info['gender']))
            table.add_row((bold('ID del Paciente:'), diagnostic_info['patient_id']))

    with doc.create(Section('Diagnóstico')):
        with doc.create(Subsection(diagnostic_info['title'])):
            doc.append(diagnostic_info['description'])

    tex_file = os.path.join('static', pdf_filename.replace('.pdf', ''))
    pdf_path = os.path.join('static', pdf_filename)
    doc.generate_tex(tex_file)

    try:
        subprocess.run(['pdflatex', '-output-directory=static', tex_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al compilar el documento: {e}")

    if os.path.exists(tex_file):
        os.remove(tex_file)
    if os.path.exists(tex_file.replace('.tex', '.log')):
        os.remove(tex_file.replace('.tex', '.log'))
    if os.path.exists(tex_file.replace('.tex', '.aux')):
        os.remove(tex_file.replace('.tex', '.aux'))

@diagnostic.route('/get-diagnostic/<patient_id>', methods=['GET'])
def get_diagnostic(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT title, description,is_generated  FROM diagnostics WHERE patient_id = %s AND user_id = %s', (patient_id, session['user_id']))
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

@diagnostic.route('/update-diagnostic', methods=['POST'])
def update_diagnostic():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    data = request.json
    patient_id = data.get('patient_id')
    title = data.get('title')
    description = data.get('description')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE diagnostics SET title = %s, description = %s WHERE patient_id = %s AND user_id = %s',
                       (title, description, patient_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Diagnóstico actualizado exitosamente'})

    except Exception as e:
        print("Error al actualizar el diagnóstico:", str(e))
        return jsonify({"error": "Error al actualizar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500


