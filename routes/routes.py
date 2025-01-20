import smtplib

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import secrets
import base64
import json
import threading
import os
from pylatex import Document, Section, Tabular, Command, Figure, Package, Subsection
from pylatex.utils import NoEscape, bold
import subprocess
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session
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
from DataBase import get_db_connection

# Crear un Blueprint
routes = Blueprint('routes', __name__)

@routes.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
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
    cursor.execute(
        'INSERT INTO password_reset_tokens (user_id, token, expiration) VALUES (%s, %s, %s)',
        (user['id'], token, expiration)
    )
    conn.commit()
    cursor.close()
    conn.close()

    send_reset_email(email, token)

    return jsonify({'message': 'Password reset link has been sent to your email'})
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

@routes.route('/reset-password/<token>', methods=['POST'])
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
@routes.route('/generate-reset-token', methods=['POST'])
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

@routes.route('/submit-feedbackE/<patient_id>', methods=['POST'])
def submit_feedback(patient_id):
    data = request.json
    ayudo_ia = data.get('ayudo_ia')  # Se asume que recibimos un valor booleano
    comentarios_adicionales = data.get('comentarios_adicionales', '')  # Comentarios opcionales

    # Verifica si el paciente existe
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM patients WHERE patient_id = %s', (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Guardar la encuesta en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO surveys (patient_id, ayudo_ia, comentarios_adicionales) '
        'VALUES (%s, %s, %s)',
        (patient_id, ayudo_ia, comentarios_adicionales)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Feedback submitted successfully'})

