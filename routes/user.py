
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, make_response, session, \
    Blueprint
from DataBase import create_tables, get_db_connection
from psycopg2.extras import RealDictCursor

user = Blueprint('user', __name__)
@user.route('/users', methods=['GET'])
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