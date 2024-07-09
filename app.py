import io
import os
import sys
import imageio
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv3D, Conv3DTranspose, Dropout, MaxPooling3D, concatenate
from UNET import dice_coef
from UNET import dice_coef_edema
from UNET import dice_coef_necrotic
from UNET import dice_coef_enhancing
from UNET import precision
from UNET import sensitivity
from UNET import specificity
from UNET import UNet
from H5 import load_hdf5_file
from moviepy.editor import ImageSequenceClip
app = Flask(__name__)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
# Define las funciones de métricas personalizadas

# Crear el modelo y cargar los pesos
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 4
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/model_3D/Final/modelUnet3D.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para manejar la predicción
@app.route('/predict', methods=['POST'])
def predict():
    if not model_loaded:
        return "Error al cargar el modelo."

    try:
        # Asegurarse de que se envió un archivo
        if 'file' not in request.files:
            return "No se envió ningún archivo."

        file = request.files['file']
        file_path = "temp_file.h5"
        file.save(file_path)

        # Cargar la imagen y realizar la predicción
        test_img, _ = load_hdf5_file(file_path)
        if test_img is None:
            return "Error al cargar el archivo HDF5."

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # Crear una lista para almacenar las imágenes del video
        images = []

        # Generar imágenes para cada slice y agregarlas a images
        for i in range(test_prediction_argmax.shape[2]):
            fig, ax = plt.subplots(1, 2, figsize=(12, 8))

            ax[0].imshow(test_img[:, :, i, 1], cmap='gray')
            ax[0].title.set_text('Testing Image')

            ax[1].imshow(test_prediction_argmax[:, :, i])
            ax[1].title.set_text('Prediction on test image')

            # Guardar la figura en un buffer de bytes
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            # Cerrar la figura para liberar memoria
            plt.close(fig)

            # Agregar la imagen al arreglo de imágenes
            images.append(image)

        # Crear un clip de video con las imágenes
        video_filename = "static/temp_video.mp4"
        clip = ImageSequenceClip(images, fps=1)
        clip.write_videofile(video_filename, codec='libx264', audio=False)

        # Eliminar archivos temporales
        os.remove(file_path)

        # Redirigir a la página de resultados
        return redirect(url_for('result', video_filename="temp_video.mp4"))

    except Exception as e:
        # Imprimir el error por consola
        print("Error durante la predicción:", str(e))
        return "Error durante la predicción. Consulta los registros del servidor para más detalles."

@app.route('/result')
def result():
    video_filename = request.args.get('video_filename')
    video_url = url_for('static', filename=video_filename)
    print(f"Video URL: {video_url}")
    return render_template('result.html', video_url=video_url)

if __name__ == "__main__":
    app.run(debug=True)