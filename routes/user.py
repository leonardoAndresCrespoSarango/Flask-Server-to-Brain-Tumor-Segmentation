
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
from psycopg2.extras import RealDictCursor

# Crear un Blueprint para la gestión de usuarios
user = Blueprint('user', __name__)

# Ruta para obtener todos los usuarios de la base de datos
@user.route('/users', methods=['GET'])
def get_users():
    # Verificamos si el usuario está autenticado mediante la existencia de 'user_id' en la sesión
    if 'user_id' not in session:
        # Si no está autenticado, respondemos con un error de autorización (401)
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        # Conectamos a la base de datos
        conn = get_db_connection()
        # Realizamos la consulta SQL para obtener usuarios
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, username, nombre FROM users')  # Incluir la columna 'name'
        users = cursor.fetchall()

        # Cerramos el cursor y la conexión a la base de datos
        cursor.close()
        conn.close()

        # Respondemos con los datos de los usuarios en formato JSON
        return jsonify(users)

    except Exception as e:
        print("Error al recuperar los usuarios:", str(e))
        return jsonify({"error": "Error al recuperar los usuarios. Consulta los registros del servidor para más detalles."}), 500