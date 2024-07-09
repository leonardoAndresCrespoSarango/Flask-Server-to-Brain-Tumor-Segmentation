import io
import sys
import imageio
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request, render_template, send_file
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

        # Cargar la imagen y realizar la predicción
        test_img, _ = load_hdf5_file(file)
        if test_img is None:
            return "Error al cargar el archivo HDF5."

        test_img_input = np.expand_dims(test_img, axis=0)
        test_prediction = model.predict(test_img_input)
        test_prediction_argmax = np.argmax(test_prediction, axis=4)[0, :, :, :]

        # Crear una lista para almacenar las imágenes del GIF
        gif_images = []

        # Generar imágenes para cada slice y agregarlas a gif_images
        for i in range(test_prediction_argmax.shape[2]):
            fig, ax = plt.subplots(1, 2, figsize=(12, 8))

            ax[0].imshow(test_img[:, :, i, 1], cmap='gray')
            ax[0].title.set_text('Testing Image')

            ax[1].imshow(test_prediction_argmax[:, :, i])
            ax[1].title.set_text('Prediction on test image')

            # Agregar la imagen actual a la lista para el GIF
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            gif_images.append(image)

            # Cerrar la figura para liberar memoria
            plt.close(fig)

        # Guardar las imágenes como un GIF en memoria
        gif_bytes = imageio.mimwrite(imageio.RETURN_BYTES, gif_images, format='GIF', fps=20)

        # Enviar el GIF como respuesta
        return send_file(io.BytesIO(gif_bytes), mimetype='image/gif')

    except Exception as e:
        # Imprimir el error por consola
        print("Error durante la predicción:", str(e))
        return "Error durante la predicción. Consulta los registros del servidor para más detalles."

if __name__ == "__main__":
    app.run(debug=True)