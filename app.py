import io
import os
import sys
import imageio
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from skimage.transform import resize
import h5py
import glob
from werkzeug.utils import secure_filename
import nibabel as nib
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
app.config['UPLOAD_FOLDER'] = 'uploads/'
path="uploads/"

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 4
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('model_3D\Final\modelUnet3D.h5')
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
        # Especificar la ruta de la carpeta que contiene los archivos HDF5
        folder_path = "processed_files/"  # Cambia esto a la ruta de tu carpeta

        # Buscar cualquier archivo HDF5 en la carpeta
        hdf5_files = glob.glob(os.path.join(folder_path, "*.h5"))

        if not hdf5_files:
            return "No se encontraron archivos HDF5 en la carpeta especificada."

        # Usar el primer archivo HDF5 encontrado
        file_path = hdf5_files[0]

        # Verificar si el archivo existe (aunque esto no debería ser necesario ya que glob ya encontró el archivo)
        if not os.path.isfile(file_path):
            return "Archivo HDF5 no encontrado."

        # Cargar la imagen y realizar la predicción
        test_img= load_hdf5_file(file_path)
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
        clip = ImageSequenceClip(images, fps=30)
        clip.write_videofile(video_filename, codec='libx264', audio=False)

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


# Ruta para manejar la subida y procesamiento de archivos
@app.route('/upload', methods=['POST'])
def upload_and_process_files():
    if 'files' not in request.files:
        return 'No files part in the request.', 400
    
    upload_files = request.files.getlist('files')
    
    mainPath = app.config['UPLOAD_FOLDER']
    for file in upload_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(mainPath, filename))
    
    t1_path = os.path.join(mainPath, '*t1n.nii.gz')
    t2_path = os.path.join(mainPath, '*t2W.nii.gz')
    t1ce_path = os.path.join(mainPath, '*t1c.nii.gz')
    flair_path = os.path.join(mainPath, '*t2f.nii.gz')
    
    t1_list = sorted(glob.glob(t1_path))
    t2_list = sorted(glob.glob(t2_path))
    t1ce_list = sorted(glob.glob(t1ce_path))
    flair_list = sorted(glob.glob(flair_path))
    
    scaler = MinMaxScaler()
    target_shape = (128, 128, 128)  # Dimensiones objetivo

    output_path = 'processed_files/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for img in range(len(t1ce_list)):
        print("Now preparing image number: ", img)
        
        temp_image_t1 = nib.load(t1_list[img]).get_fdata()
        temp_image_t1 = scaler.fit_transform(temp_image_t1.reshape(-1, temp_image_t1.shape[-1])).reshape(temp_image_t1.shape)

        temp_image_t2 = nib.load(t2_list[img]).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)
        
        temp_image_t1ce = nib.load(t1ce_list[img]).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)
    
        temp_image_flair = nib.load(flair_list[img]).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)
            
        temp_combined_images = np.stack([temp_image_t1, temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)
        
        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)
        
        with h5py.File(os.path.join(output_path, f'patient_{img}.h5'), 'w') as hf:
            hf.create_dataset('images', data=temp_combined_images_resized, compression='gzip')
    
        print(f"Imágenes guardadas para el paciente {img} como HDF5")
    
    # Eliminar archivos temporales
    files_to_delete = glob.glob(os.path.join(path, '*.nii.gz'))
    for file in files_to_delete:
        os.remove(file)
    
    return 'Files processed and saved.', 200


if __name__ == "__main__":
    app.run(debug=True)