import base64
import io
import json
import os

from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import threading
import os
from pylatex import Document, Section, Tabular, Command, Figure, Package, Subsection
from pylatex.utils import NoEscape, bold
import subprocess
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session
import sys

import plotly.graph_objects as go
import plotly.subplots as psub
import numpy as np
from skimage import measure
from sklearn.preprocessing import MinMaxScaler
from skimage.transform import resize
import h5py
import glob
import dash
from dash.dependencies import Input, Output
from flask import Flask, jsonify, request, session, render_template_string
from dash import dcc, html
import plotly.express as px
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import nibabel as nib
import matplotlib.pyplot as plt
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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['STATIC_FOLDER'] = 'static/'
path = "uploads/"
secret_key = os.urandom(24)
print(secret_key)
app.secret_key =secret_key



#funcion para elimunar
def delete_file_after_delay(file_path, delay):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")

    timer = threading.Timer(delay, delete_file)
    timer.start()
#conexion con la base de datos postgreSQL
# Configurar la conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres.txfhmfkxzcwigxhzhvmx',
        password='VLNVddyd2002',
        host='aws-0-us-east-1.pooler.supabase.com',
        port='6543'
    )

    return conn
# Verificar si la tabla users existe y crearla si no
# Verificar si la tabla users existe y crearla si no
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    CREATE TABLE IF NOT EXISTS predictions (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL,
        patient_name VARCHAR(255) NOT NULL,
        patient_age INT NOT NULL,
        patient_gender VARCHAR(10) NOT NULL,
        prediagnosis TEXT NOT NULL,
        video BYTEA NOT NULL,
        report BYTEA NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS patients (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL UNIQUE,
        numero_historia_clinica VARCHAR(255) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        token VARCHAR(255) NOT NULL,
        expiration TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS diagnostics (
        id SERIAL PRIMARY KEY,
        patient_id VARCHAR(255) NOT NULL,
        user_id INT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );
    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        patient_id VARCHAR(255) NOT NULL,
        report_text2 TEXT NOT NULL,
        report_text5 TEXT NOT NULL,
        graph2_image_path TEXT NOT NULL,
        graph5_image_path TEXT NOT NULL,
        feedback JSON NOT NULL,
        modalities_description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Llamar a la función para crear las tablas al iniciar la aplicación
create_tables()

# Llamar a la función para crear las tablas al iniciar la aplicación
create_tables()


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')  # Obtener el nombre del usuario

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, nombre) VALUES (%s, %s, %s)', (email, hashed_password, name))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully'})



# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        session['user_id'] = user['id']
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'name': user['nombre']
        })
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/predictions', methods=['GET'])
def get_predictions():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, patient_id, patient_name, patient_age, patient_gender, prediagnosis FROM predictions WHERE user_id = %s', (user_id,))
        predictions = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(predictions)

    except Exception as e:
        print("Error al recuperar las predicciones:", str(e))
        return jsonify({"error": "Error al recuperar las predicciones. Consulta los registros del servidor para más detalles."}), 500
@app.route('/predictions/<int:prediction_id>/video', methods=['GET'])
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

@app.route('/predictions/<int:prediction_id>/report', methods=['GET'])
def get_prediction_report(prediction_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT report FROM predictions WHERE id = %s AND user_id = %s', (prediction_id, session['user_id']))
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
@app.route('/users', methods=['GET'])
def get_users():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, username, nombre FROM users')  # Incluir la columna 'name'
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(users)

    except Exception as e:
        print("Error al recuperar los usuarios:", str(e))
        return jsonify({"error": "Error al recuperar los usuarios. Consulta los registros del servidor para más detalles."}), 500
#-----------------------------------------------RECUPERACION DE CONTRASEÑA----------------------------------------------------------------------#
def send_reset_email(email, token):
    sender = 'youremail@example.com'
    password = 'yourpassword'
    subject = 'Password Reset Request'
    body = f'Please use the following link to reset your password: http://localhost:4200/reset-password/{token}'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    token = secrets.token_urlsafe(16)
    expiration = datetime.utcnow() + timedelta(hours=1)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO password_reset_tokens (user_id, token, expiration) VALUES (%s, %s, %s)',
                   (user['id'], token, expiration))
    conn.commit()
    cursor.close()
    conn.close()

    send_reset_email(email, token)

    return jsonify({'message': 'Password reset link has been sent to your email'})


@app.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.json
    new_password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM password_reset_tokens WHERE token = %s', (token,))
    reset_token = cursor.fetchone()

    if not reset_token or reset_token['expiration'] < datetime.utcnow():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Invalid or expired token'}), 400

    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, reset_token['user_id']))
    cursor.execute('DELETE FROM password_reset_tokens WHERE token = %s', (token,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Password has been reset successfully'})
@app.route('/generate-reset-token', methods=['POST'])
def generate_reset_token():
    data = request.json
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    token = secrets.token_urlsafe(16)
    expiration = datetime.utcnow() + timedelta(hours=1)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO password_reset_tokens (user_id, token, expiration) VALUES (%s, %s, %s)', (user['id'], token, expiration))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'token': token, 'message': 'Reset token generated successfully'})

#---------------------------------------------------------------------------#
#registro de pacientes:
@app.route('/add-patient', methods=['POST'])
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

@app.route('/patients', methods=['GET'])
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

# Ruta para agregar diagnóstico
@app.route('/add-diagnostic', methods=['POST'])
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
        cursor.execute(
            'INSERT INTO diagnostics (patient_id, user_id, title, description) VALUES (%s, %s, %s, %s)',
            (diagnostic_info['patient_id'], user_id, diagnostic_info['title'], diagnostic_info['description'])
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Diagnóstico agregado exitosamente'})

    except Exception as e:
        print("Error al agregar el diagnóstico:", str(e))
        return jsonify({"error": "Error al agregar el diagnóstico. Consulta los registros del servidor para más detalles."}), 500

# Ruta para obtener diagnósticos de un paciente
@app.route('/diagnostics/<patient_id>', methods=['GET'])
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

@app.route('/generate-diagnostic-pdf', methods=['POST'])
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

@app.route('/get-diagnostic/<patient_id>', methods=['GET'])
def get_diagnostic(patient_id):
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT title, description FROM diagnostics WHERE patient_id = %s AND user_id = %s', (patient_id, session['user_id']))
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

@app.route('/update-diagnostic', methods=['POST'])
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








#------------------------------------------------------------------------------------#
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 3
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('model_3D\\3 clases\\modelUnet3D_3.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user_id = session['user_id']

    try:
        # Verificar el tipo de contenido de la solicitud
        if request.content_type != 'application/json':
            return jsonify({"error": "Tipo de contenido no soportado"}), 415

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        patient_info = {
            'name': data['name'],
            'age': data['age'],
            'gender': data['gender'],
            'id': data['patientId']
        }

        prediagnosis = data['diagnosis']

        folder_path = "processed_files/"
        hdf5_files = glob.glob(os.path.join(folder_path, "*.h5"))

        if not hdf5_files:
            return jsonify({"error": "No se encontraron archivos HDF5 en la carpeta especificada."}), 404

        file_path = hdf5_files[0]

        if not os.path.isfile(file_path):
            return jsonify({"error": "Archivo HDF5 no encontrado."}), 404

        test_img = load_hdf5_file(file_path)
        if test_img is None:
            return jsonify({"error": "Error al cargar el archivo HDF5."}), 500

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        images = []

        for i in range(test_prediction_argmax.shape[2]):
            fig, ax = plt.subplots(1, 2, figsize=(12, 8))

            ax[0].imshow(test_img[:, :, i, 1], cmap='gray')
            ax[0].title.set_text('Testing Image')

            ax[1].imshow(test_prediction_argmax[:, :, i])
            ax[1].title.set_text('Prediction on test image')

            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            plt.close(fig)

            images.append(image)

            temp_image_path = f"static/temp_image_{i}.png"
            plt.imsave(temp_image_path, image)

        video_filename = f"static/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        clip = ImageSequenceClip(images, fps=20)
        clip.write_videofile(video_filename, codec='libx264', audio=False)

        mri_images = [f"static/temp_image_{i}.png" for i in range(len(images))]

        report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        create_medical_report(patient_info, prediagnosis, mri_images, report_filename)

        with open(video_filename, 'rb') as video_file:
            video_data = video_file.read()

        with open(report_filename, 'rb') as report_file:
            report_data = report_file.read()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO predictions (user_id, patient_id, patient_name, patient_age, patient_gender, prediagnosis, video, report) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (user_id, patient_info['id'], patient_info['name'], patient_info['age'], patient_info['gender'],
             prediagnosis, psycopg2.Binary(video_data), psycopg2.Binary(report_data))
        )
        conn.commit()
        cursor.close()
        conn.close()

        delete_file_after_delay(video_filename, 600)
        os.remove(report_filename)
        video_url = f"{request.host_url}{video_filename}"
        return jsonify({"video_url": video_url})

    except Exception as e:
        print("Error durante la predicción:", str(e))
        return jsonify({"error": "Error durante la predicción. Consulta los registros del servidor para más detalles."}), 500

@app.route('/result')
def result():
    video_filename = request.args.get('video_filename')
    video_url = url_for('static', filename=video_filename)
    print(f"Video URL: {video_url}")
    response = make_response(render_template('result.html', video_url=video_url))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# Ruta para manejar la subida y procesamiento de archivos
@app.route('/upload', methods=['POST'])
def upload_and_process_files():
    if 'files' not in request.files or 'patient_id' not in request.form:
        response = make_response('No files part or patient ID in the request.', 400)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    upload_files = request.files.getlist('files')
    patient_id = request.form['patient_id']

    # Añadir mensaje de depuración
    print(f"Patient ID received: {patient_id}")

    mainPath = app.config['UPLOAD_FOLDER']
    for file in upload_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(mainPath, filename))
        print(f"Archivo guardado: {filename}")

    # Verificar el contenido del directorio uploads
    print(f"Contenido de {mainPath}: {os.listdir(mainPath)}")

    t2_path = os.path.join(mainPath, '*t2W.nii.gz')
    t1ce_path = os.path.join(mainPath, '*t1c.nii.gz')
    flair_path = os.path.join(mainPath, '*t2f.nii.gz')

    print(f"Buscando archivos T2 en: {t2_path}")
    print(f"Buscando archivos T1CE en: {t1ce_path}")
    print(f"Buscando archivos FLAIR en: {flair_path}")

    t2_list = sorted(glob.glob(t2_path))
    t1ce_list = sorted(glob.glob(t1ce_path))
    flair_list = sorted(glob.glob(flair_path))

    print(f"Archivos T2 encontrados: {t2_list}")
    print(f"Archivos T1CE encontrados: {t1ce_list}")
    print(f"Archivos FLAIR encontrados: {flair_list}")

    if len(t1ce_list) == 0 or len(t2_list) == 0 or len(flair_list) == 0:
        print("Error: Required files are missing")
        return jsonify({'message': 'Error: Required files are missing'}), 400

    scaler = MinMaxScaler()
    target_shape = (128, 128, 128)  # Dimensiones objetivo

    output_path = 'processed_files/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    h5_filename = os.path.join(output_path, f'{patient_id}.h5')

    images = []
    for img in range(len(t1ce_list)):
        print("Now preparing image number: ", img)

        temp_image_t2 = nib.load(t2_list[img]).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)

        temp_image_t1ce = nib.load(t1ce_list[img]).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)

        temp_image_flair = nib.load(flair_list[img]).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)

        temp_combined_images = np.stack([temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)

        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)
        for i in range(temp_combined_images_resized.shape[2]):
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].imshow(temp_combined_images_resized[:, :, i, 0], cmap='gray')
            axes[0].set_title('T1CE')
            axes[1].imshow(temp_combined_images_resized[:, :, i, 1], cmap='gray')
            axes[1].set_title('T2')
            axes[2].imshow(temp_combined_images_resized[:, :, i, 2], cmap='gray')
            axes[2].set_title('FLAIR')
            for ax in axes:
                ax.axis('off')
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            plt.close(fig)
            images.append(image)

        try:
            with h5py.File(h5_filename, 'w') as hf:
                hf.create_dataset('images', data=temp_combined_images_resized, compression='gzip')
            print(f"Imágenes guardadas para el paciente {patient_id} como HDF5")
        except Exception as e:
            print(f"Error al guardar el archivo HDF5: {e}")
            return jsonify({'message': 'Error al guardar el archivo HDF5'}), 500

    # Verificar si el archivo HDF5 fue creado correctamente
    if os.path.exists(h5_filename):
        print(f"Archivo HDF5 {h5_filename} creado exitosamente.")
        return jsonify({'message': 'Archivos cargados y procesados exitosamente. Las imágenes han sido guardadas como HDF5.'})
    else:
        print(f"Error: El archivo HDF5 {h5_filename} no fue creado.")
        return jsonify({'message': f'Error: El archivo HDF5 {h5_filename} no fue creado.'}), 500


#prediccion con ia
@app.route('/predict-ia', methods=['POST'])
def predict_ia():
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    h5_filename = os.path.join('processed_files', f'{patient_id}.h5')

    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

    try:
        test_img = load_hdf5_file(h5_filename)
        if test_img is None:
            return jsonify({'message': 'Error al cargar el archivo HDF5.'}), 500

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # Generar las gráficas
        graph1_html = generate_graph1(test_img, test_prediction_argmax)
        graph2_html, report_text2 = generate_graph2(test_prediction_argmax)
        graph3_html = generate_graph3(test_img, test_prediction_argmax)
        graph4_html = generate_graph4(test_img, test_prediction_argmax)
        graph5_html, report_text5 = generate_graph5(test_img, test_prediction_argmax)
        graph6_html = generate_graph6(test_img, test_prediction_argmax)

        graph1_url = url_for('static', filename=graph1_html, _external=True)
        graph2_url = url_for('static', filename=graph2_html, _external=True)
        graph3_url = url_for('static', filename=graph3_html, _external=True)
        graph4_url = url_for('static', filename=graph4_html, _external=True)
        graph5_url = url_for('static', filename=graph5_html, _external=True)
        graph6_url = url_for('static', filename=graph6_html, _external=True)

        return jsonify({
            "html_url1": graph1_url,
            "html_url2": graph2_url,
            "html_url3": graph3_url,
            "html_url4": graph4_url,
            "html_url5": graph5_url,
            "html_url6": graph6_url,
            "report_text2": report_text2,
            "report_text5": report_text5
        })

    except Exception as e:
        print(f"Error durante la predicción: {str(e)}")
        return jsonify({"message": "Error durante la predicción. Consulta los registros del servidor para más detalles."}), 500

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

@app.route('/send-report', methods=['POST'])
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

@app.route('/download-report/<patient_id>', methods=['GET'])
def download_report(patient_id):
    try:
        temp_pdf_path = f'reporte_paciente_{patient_id}.pdf'
        return send_file(temp_pdf_path, as_attachment=True, download_name=f'reporte_paciente_{patient_id}.pdf', mimetype='application/pdf')
    except Exception as e:
        print(f"Error al descargar el reporte: {e}")
        return jsonify({"error": "Error al descargar el reporte"}), 500

#leonardo
@app.route('/generate-graph6', methods=['POST'])
def generate_graph6_route():
    if 'user_id' not in session:
        return jsonify({"message": "Usuario no autenticado"}), 401

    user_id = session['user_id']
    patient_id = request.json.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is missing'}), 400

    h5_filename = os.path.join('processed_files', f'{patient_id}.h5')

    if not os.path.exists(h5_filename):
        return jsonify({'message': f'El archivo HDF5 {h5_filename} no fue encontrado.'}), 404

    try:
        # Cargar las imágenes desde el archivo HDF5
        test_img = load_hdf5_file(h5_filename)
        if test_img is None:
            return jsonify({'message': 'Error al cargar el archivo HDF5.'}), 500

        # Generar la gráfica 6 (solo imágenes del paciente)
        graph6_html = generate_graph6_no_prediction(test_img)

        # Generar la URL para la gráfica
        graph6_url = url_for('static', filename=graph6_html, _external=True)

        return jsonify({
            "html_url6": graph6_url
        })

    except Exception as e:
        print(f"Error al generar la gráfica 6: {str(e)}")
        return jsonify({"message": "Error al generar la gráfica 6. Consulta los registros del servidor para más detalles."}), 500

if __name__ == "__main__":
    app.run(debug=True)
