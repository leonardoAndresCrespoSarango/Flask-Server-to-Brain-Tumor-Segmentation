import os
from flask import Flask, render_template, make_response
import sys
from Artificial_Intelligence_Brats.AI_BraTs_Function_predict import predictionBrats, predictionBratsAI
from Artificial_Intelligence_Brats.AI_BraTs_Function_report import report
from Artificial_Intelligence_Brats.AI_BraTs_Function_result import resultVideo
from Artificial_Intelligence_Brats.AI_BraTs_Function_upload_N_ProcessFile import upload
from DataBase import create_tables
from UNET import UNet
from diagnostic import diagnostic, diagnostic_patient
from patient import patient
from routes import routes, prediction, user
from routes.login import loginApp as login_blueprint

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['STATIC_FOLDER'] = 'static/'
path = "uploads/"
secret_key = os.urandom(24)
print(secret_key)
app.secret_key =secret_key


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
#funcion para elimunar
# llama a la Base de datos para su creacion
create_tables()

app.register_blueprint(routes)
app.register_blueprint(login_blueprint)
app.register_blueprint(prediction)
app.register_blueprint(user)
app.register_blueprint(patient)
app.register_blueprint(diagnostic)
#------------------------------------------------------------------------------------#
#sys.stdin.reconfigure(encoding='utf-8')
#sys.stdout.reconfigure(encoding='utf-8')
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

app.register_blueprint(predictionBrats)
app.register_blueprint(resultVideo)
app.register_blueprint(upload)
#prediccion con ia
app.register_blueprint(predictionBratsAI)
app.register_blueprint(report)
app.register_blueprint(diagnostic_patient)
if __name__ == "__main__":
    app.run(debug=True)
