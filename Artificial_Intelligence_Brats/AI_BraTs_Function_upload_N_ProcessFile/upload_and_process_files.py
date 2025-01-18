import os
from flask import jsonify, request, make_response, Blueprint, current_app
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from skimage.transform import resize
import h5py
import glob
from werkzeug.utils import secure_filename
import nibabel as nib
import matplotlib.pyplot as plt
upload = Blueprint('upload', __name__)
@upload.route('/upload', methods=['POST'])
def upload_and_process_files():
    if 'files' not in request.files or 'patient_id' not in request.form:
        response = make_response('No files part or patient ID in the request.', 400)
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    upload_files = request.files.getlist('files')
    patient_id = request.form['patient_id']

    print(f"Files received: {[file.filename for file in upload_files]}")
    print(f"Patient ID received: {patient_id}")

    mainPath = current_app.config['UPLOAD_FOLDER']
    for file in upload_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(mainPath, filename))
        print(f"Archivo guardado: {filename}")

    # Verificar el contenido del directorio uploads
    print(f"Contenido de {mainPath}: {os.listdir(mainPath)}")

    t2_path = os.path.join(mainPath, '*t2W.nii.gz')
    t1ce_path = os.path.join(mainPath, '*t1c.nii.gz')
    flair_path = os.path.join(mainPath, '*t2f.nii.gz')

    print(f"Buscando archivos T2 en: {t2_path}")
    print(f"Buscando archivos T1CE en: {t1ce_path}")
    print(f"Buscando archivos FLAIR en: {flair_path}")

    t2_list = sorted(glob.glob(t2_path))
    t1ce_list = sorted(glob.glob(t1ce_path))
    flair_list = sorted(glob.glob(flair_path))

    print(f"Archivos T2 encontrados: {t2_list}")
    print(f"Archivos T1CE encontrados: {t1ce_list}")
    print(f"Archivos FLAIR encontrados: {flair_list}")

    if len(t1ce_list) == 0 or len(t2_list) == 0 or len(flair_list) == 0:
        print("Error: Required files are missing")
        return jsonify({'message': 'Error: Required files are missing'}), 400

    scaler = MinMaxScaler()
    target_shape = (128, 128, 128)  # Dimensiones objetivo

    output_path = 'processed_files/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    h5_filename = os.path.join(output_path, f'{patient_id}.h5')

    images = []
    for img in range(len(t1ce_list)):
        print("Now preparing image number: ", img)

        temp_image_t2 = nib.load(t2_list[img]).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)

        temp_image_t1ce = nib.load(t1ce_list[img]).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)

        temp_image_flair = nib.load(flair_list[img]).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)

        temp_combined_images = np.stack([temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)

        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)
        for i in range(temp_combined_images_resized.shape[2]):
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            axes[0].imshow(temp_combined_images_resized[:, :, i, 0], cmap='gray')
            axes[0].set_title('T1CE')
            axes[1].imshow(temp_combined_images_resized[:, :, i, 1], cmap='gray')
            axes[1].set_title('T2')
            axes[2].imshow(temp_combined_images_resized[:, :, i, 2], cmap='gray')
            axes[2].set_title('FLAIR')
            for ax in axes:
                ax.axis('off')
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            plt.close(fig)
            images.append(image)

        try:
            with h5py.File(h5_filename, 'w') as hf:
                hf.create_dataset('images', data=temp_combined_images_resized, compression='gzip')
            print(f"Imágenes guardadas para el paciente {patient_id} como HDF5")
        except Exception as e:
            print(f"Error al guardar el archivo HDF5: {e}")
            return jsonify({'message': 'Error al guardar el archivo HDF5'}), 500

    # Verificar si el archivo HDF5 fue creado correctamente
    if os.path.exists(h5_filename):
        print(f"Archivo HDF5 {h5_filename} creado exitosamente.")
        return jsonify({'message': 'Archivos cargados y procesados exitosamente. Las imágenes han sido guardadas como HDF5.'})
    else:
        print(f"Error: El archivo HDF5 {h5_filename} no fue creado.")
        return jsonify({'message': f'Error: El archivo HDF5 {h5_filename} no fue creado.'}), 500
