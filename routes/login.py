from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
from psycopg2.extras import RealDictCursor
import bcrypt

#Blueprint para organizar el modulo de login
loginApp = Blueprint('loginApp', __name__)

# Ruta para registrar un nuevo usuario
@loginApp.route('/register', methods=['POST'])
def register():
    # Obtención de los datos enviados en formato JSON
    data = request.json
    email = data.get('email')# Correo electrónico del usuario
    password = data.get('password')# Contraseña del usuario
    name = data.get('name')  # Obtener el nombre del usuario

    # Encriptación de la contraseña utilizando bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Inserción de un nuevo usuario en la base de datos
    cursor.execute('INSERT INTO users (username, password, nombre) VALUES (%s, %s, %s)', (email, hashed_password, name))
    conn.commit()
    cursor.close()
    conn.close()

    # Respuesta JSON indicando que el registro fue exitoso
    return jsonify({'message': 'User registered successfully'})



# Ruta para iniciar sesión
@loginApp.route('/login', methods=['POST'])
def login():
    # Obtención de los datos de login (email y contraseña)
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Conexión a la base de datos para verificar las credenciales
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    # Verificación de la contraseña utilizando bcrypt
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # Si la contraseña es correcta, almacenamos el ID de usuario en la sesión
        session['user_id'] = user['id']
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'name': user['nombre']
        })
    else:
        # Si las credenciales son incorrectas, devolvemos un error
        return jsonify({'message': 'Invalid email or password'}), 401

# Ruta para cerrar sesión
@loginApp.route('/logout', methods=['POST'])
def logout():
    # Eliminamos el ID de usuario de la sesión, cerrando la sesión
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

# Ruta para obtener las predicciones del usuario
@loginApp.route('/predictions', methods=['GET'])
def get_predictions():
    # Verificamos si el usuario está autenticado (si su ID está en la sesión)
    if 'user_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    # Recuperamos el ID del usuario de la sesión
    user_id = session['user_id']

    try:
        # Conexión a la base de datos para obtener las predicciones
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