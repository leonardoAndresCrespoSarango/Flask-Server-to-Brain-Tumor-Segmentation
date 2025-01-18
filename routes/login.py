from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
from psycopg2.extras import RealDictCursor
import bcrypt
loginApp = Blueprint('loginApp', __name__)
@loginApp.route('/register', methods=['POST'])
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
@loginApp.route('/login', methods=['POST'])
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

@loginApp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@loginApp.route('/predictions', methods=['GET'])
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