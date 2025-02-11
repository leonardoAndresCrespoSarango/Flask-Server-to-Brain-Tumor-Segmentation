from flask import Flask, jsonify, request, render_template, send_file, url_for, make_response, session, Blueprint

# Crear un Blueprint para manejar las rutas relacionadas con los resultados de video
resultVideo = Blueprint('resultVideo', __name__)

# Ruta para mostrar la página de resultados con el video
@resultVideo.route('/result')
def result():
    # Obtener el nombre del archivo de video pasado como parámetro en la URL
    video_filename = request.args.get('video_filename')

    # Generar la URL del archivo de video usando url_for para acceder al archivo estático
    video_url = url_for('static', filename=video_filename)
    print(f"Video URL: {video_url}")

    # Crear la respuesta HTTP que renderiza el template 'result.html' y pasa la URL del video
    response = make_response(render_template('result.html', video_url=video_url))

    # Agregar encabezados de control de acceso CORS (Cross-Origin Resource Sharing)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # Retornar la respuesta con los encabezados y el contenido de la página
    return response