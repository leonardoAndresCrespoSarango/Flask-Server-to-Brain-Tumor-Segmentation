from flask import Flask, jsonify, request, render_template, send_file, url_for, make_response, session, Blueprint

resultVideo = Blueprint('resultVideo', __name__)
@resultVideo.route('/result')
def result():
    video_filename = request.args.get('video_filename')
    video_url = url_for('static', filename=video_filename)
    print(f"Video URL: {video_url}")
    response = make_response(render_template('result.html', video_url=video_url))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response