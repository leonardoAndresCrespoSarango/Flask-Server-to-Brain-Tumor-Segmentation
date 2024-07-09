import os
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
from H5 import load_hdf5_file  # Importa tu función para cargar archivos HDF5
import joblib

# Cargar el modelo y los pesos
from UNET import UNet  # Asegúrate de importar adecuadamente tu modelo UNet

IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS = 128, 128, 128, 4
num_classes = 4

try:
    model = UNet(IMG_HEIGHT, IMG_WIDTH, IMG_DEPTH, IMG_CHANNELS, num_classes)
    model.load_weights('C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/model_3D/Final/modelUnet3D.h5')
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

# Cargar el pipeline
pipeline = joblib.load('C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/cuadernos de prueba/image_processing_pipeline.pkl')

def transform_and_predict(data_folder, output_path):
    try:
        # Aplicar el pipeline al conjunto de datos
        pipeline.transform(data_folder)

        # Preparar para la predicción
        video_filename = None
        for img_file in os.listdir(output_path):
            if img_file.endswith(".h5"):
                file_path = os.path.join(output_path, img_file)
                test_img, _ = load_hdf5_file(file_path)

                if test_img is None:
                    return None

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
                video_filename = os.path.join(output_path, "temp_video.mp4")
                clip = ImageSequenceClip(images, fps=1)
                clip.write_videofile(video_filename, codec='libx264', audio=False)

        return video_filename

    except Exception as e:
        print("Error durante la predicción:", str(e))
        return None
