import os
from flask import jsonify, request, make_response, Blueprint, current_app, session
import numpy as np
from psycopg2.extras import RealDictCursor
from sklearn.preprocessing import MinMaxScaler
from skimage.transform import resize
import h5py
import glob
from tensorflow.keras.utils import to_categorical
from werkzeug.utils import secure_filename
import nibabel as nib
import matplotlib.pyplot as plt

from DataBase import get_db_connection

#Definir el blueprint para la carga de archivos
upload = Blueprint('upload', __name__)

# Ruta para cargar y procesar archivos de imágenes
@upload.route('/upload', methods=['POST'])
def upload_and_process_files():

    # Verificar si los archivos y el patient_id están presentes en la solicitud
    if 'files' not in request.files or 'patient_id' not in request.form:
        response = make_response('No files part or patient ID in the request.', 400)

        # Agregar cabeceras CORS para permitir solicitudes desde otros orígenes
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Obtener los archivos y el ID del paciente de la solicitud
    upload_files = request.files.getlist('files')
    patient_id = request.form['patient_id']
    user_id = session.get('user_id')  # Obtén el ID del usuario autenticado

    # Verificar si el usuario está autenticado
    if not user_id:
        return jsonify({'message': 'Usuario no autenticado'}), 401
<<<<<<< HEAD

    print(f"Files received: {[file.filename for file in upload_files]}")
    print(f"Patient ID received: {patient_id}")
    print(f"User ID: {user_id}")

    # Verificar o crear la carpeta donde se guardarán los archivos cargados
=======
    
    print(f"Patient ID: {patient_id}, User ID: {user_id}")

>>>>>>> diegotesis
    mainPath = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(mainPath):
        os.makedirs(mainPath)

<<<<<<< HEAD
    # Guardar los archivos cargados en la carpeta de destino
    for file in upload_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(mainPath, filename))
        print(f"Archivo guardado: {filename}")

    # Verificar el contenido del directorio uploads
    print(f"Contenido de {mainPath}: {os.listdir(mainPath)}")

    # Buscar archivos de diferentes modalidades (T2, T1CE, FLAIR) en la carpeta cargada
    t2_path = os.path.join(mainPath, '*t2W.nii.gz')
    t1ce_path = os.path.join(mainPath, '*t1c.nii.gz')
    flair_path = os.path.join(mainPath, '*t2f.nii.gz')

    # Mostrar los paths de búsqueda
    print(f"Buscando archivos T2 en: {t2_path}")
    print(f"Buscando archivos T1CE en: {t1ce_path}")
    print(f"Buscando archivos FLAIR en: {flair_path}")

    # Obtener la lista de archivos que coinciden con las búsquedas
    t2_list = sorted(glob.glob(t2_path))
    t1ce_list = sorted(glob.glob(t1ce_path))
    flair_list = sorted(glob.glob(flair_path))

    # Imprimir las listas de archivos encontrados
    print(f"Archivos T2 encontrados: {t2_list}")
    print(f"Archivos T1CE encontrados: {t1ce_list}")
    print(f"Archivos FLAIR encontrados: {flair_list}")


    # Verificar si alguno de los archivos necesarios está ausente
    if len(t1ce_list) == 0 or len(t2_list) == 0 or len(flair_list) == 0:
        print("Error: Required files are missing")
        return jsonify({'message': 'Error: Required files are missing'}), 400

    try:
        # Conectar a la base de datos para actualizar los paths de las modalidades
        conn = get_db_connection()
        cursor = conn.cursor()

        # Actualizar los paths de las modalidades en la base de datos
        cursor.execute("""
        UPDATE patients
        SET t1ce_path = %s,
            t2_path = %s,
            flair_path = %s
        WHERE patient_id = %s AND user_id = %s;
        """, (
            t1ce_list[0] if t1ce_list else None,
            t2_list[0] if t2_list else None,
            flair_list[0] if flair_list else None,
            patient_id,
            user_id
        ))

        # Confirmar la transacción
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Paths actualizados correctamente para el paciente {patient_id}")

    except Exception as e:
        print(f"Error al guardar los paths en la base de datos: {e}")
        return jsonify({'message': 'Error al guardar los paths en la base de datos.'}), 500

    # Procesar y guardar las imágenes
    scaler = MinMaxScaler()
    target_shape = (128, 128, 128)  # Dimensiones objetivo
    output_path = 'processed_files/'

    # Verificar si la carpeta de salida existe, y si no, crearla
=======
    # Guardar archivos con prefijo patient_id y verificar que sean del paciente correcto
    saved_files = []
    for file in upload_files:
        filename = secure_filename(file.filename)
        if patient_id not in filename:
            filename = f"{patient_id}_{filename}"  # Asegura que el nombre contiene el patient_id
        file_path = os.path.join(mainPath, filename)
        file.save(file_path)
        saved_files.append(file_path)
        print(f"Archivo guardado: {file_path}")

    # Conectar a la base de datos para verificar si ya existen los paths
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT t1ce_path, t2_path, flair_path, t1_path FROM patients WHERE patient_id = %s AND user_id = %s;", 
                       (patient_id, user_id))
        existing_paths = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al verificar en la base de datos: {e}")
        return jsonify({'message': 'Error en la base de datos.'}), 500

    # Si ya están todos los archivos en la BD, evitar reprocesarlos
    if all(existing_paths):
        print(f"Los archivos para el paciente {patient_id} ya están subidos y registrados en la base de datos.")
        return jsonify({'message': 'Los archivos ya existen en la base de datos. No se realizó conversión a HDF5.'}), 200

    # Función para obtener el archivo más reciente de un paciente
    def get_latest_patient_file(pattern):
        files = glob.glob(pattern)
        patient_files = [f for f in files if patient_id in os.path.basename(f)]
        if patient_files:
            return max(patient_files, key=os.path.getmtime)  # Obtiene el archivo más reciente con patient_id
        return None

    # Buscar archivos asegurando que son del paciente correcto
    t2_file = get_latest_patient_file(os.path.join(mainPath, f"*t2W.nii.gz"))
    t1ce_file = get_latest_patient_file(os.path.join(mainPath, f"*t1c.nii.gz"))
    flair_file = get_latest_patient_file(os.path.join(mainPath, f"*t2f.nii.gz"))
    t1_file = get_latest_patient_file(os.path.join(mainPath, f"*t1n.nii.gz"))

    if not (t1ce_file and t2_file and flair_file and t1_file):
        return jsonify({'message': 'Error: Faltan archivos de modalidades.'}), 400

    print(f"T2 seleccionado: {t2_file}")
    print(f"T1CE seleccionado: {t1ce_file}")
    print(f"FLAIR seleccionado: {flair_file}")
    print(f"T1 seleccionado: {t1_file}")

    # Guardar los nuevos paths en la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients
            SET t1ce_path = %s, t2_path = %s, flair_path = %s, t1_path = %s
            WHERE patient_id = %s AND user_id = %s;
        """, (t1ce_file, t2_file, flair_file, t1_file, patient_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Paths guardados en BD para el paciente {patient_id}")
    except Exception as e:
        print(f"Error al actualizar BD: {e}")
        return jsonify({'message': 'Error al actualizar BD.'}), 500

    # Procesamiento y guardado en .h5
    scaler = MinMaxScaler()
    target_shape = (128, 128, 128)
    output_path = 'processed_files/'

>>>>>>> diegotesis
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    h5_filename = os.path.join(output_path, f'{patient_id}.h5')
<<<<<<< HEAD

    images = []
    for img in range(len(t1ce_list)):
        print("Now preparing image number: ", img)

        # Cargar y preprocesar cada modalidad
        temp_image_t2 = nib.load(t2_list[img]).get_fdata()
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)

        temp_image_t1ce = nib.load(t1ce_list[img]).get_fdata()
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)

        temp_image_flair = nib.load(flair_list[img]).get_fdata()
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)


        # Combinar las imágenes de diferentes modalidades en un solo array
        temp_combined_images = np.stack([temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)


        # Redimensionar la imagen combinada a la forma objetivo
        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)

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

=======
    h5_classification_filename = os.path.join(output_path, f'{patient_id}_to_classify.h5')

    print(f"Procesando imágenes para {patient_id}...")

    try:
        # Cargar y normalizar imágenes
        temp_image_t2 = nib.load(t2_file).get_fdata()
        temp_image_t1ce = nib.load(t1ce_file).get_fdata()
        temp_image_flair = nib.load(flair_file).get_fdata()
        temp_image_t1 = nib.load(t1_file).get_fdata()

        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)
        temp_image_t1 = scaler.fit_transform(temp_image_t1.reshape(-1, temp_image_t1.shape[-1])).reshape(temp_image_t1.shape)

        # Combinar imágenes para segmentación
        temp_combined_images = np.stack([temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)
        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)

        # Guardar en HDF5 para segmentación
        with h5py.File(h5_filename, 'w') as hf:
            hf.create_dataset('images', data=temp_combined_images_resized, compression='gzip')
        print(f"Guardado HDF5 {h5_filename}")

        # Combinar imágenes para clasificación
        temp_combined_images_4mod = np.stack([temp_image_t1, temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)
        temp_combined_images_4mod_resized = resize(temp_combined_images_4mod, target_shape, mode='constant', anti_aliasing=True)

        # Guardar en HDF5 para clasificación
        with h5py.File(h5_classification_filename, 'w') as hf:
            hf.create_dataset('images', data=temp_combined_images_4mod_resized, compression='gzip')
        print(f"Guardado HDF5 Clasificación {h5_classification_filename}")

    except Exception as e:
        print(f"Error al procesar imágenes: {e}")
        return jsonify({'message': 'Error al procesar imágenes'}), 500

    print(f"Procesamiento completado para {patient_id}.")
    return jsonify({'message': 'Archivos cargados y procesados exitosamente en HDF5.'})


# endpoint para verificar que los archivos nifti del paciente ya estan

@upload.route('/check-patient-files', methods=['POST'])
def check_patient_files():
    """ Verifica si las modalidades ya están en la base de datos para un paciente """
    print(f'sesion {session}')
    
    data = request.get_json()

    # patient_id = request.form['patient_id']
    # user_id = session.get('user_id') 

    patient_id = data.get('patient_id')
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'message': 'Usuario no autenticado'}), 401

    if not patient_id:
        return jsonify({'message': 'Falta el patient_id'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t1ce_path, t2_path, flair_path, t1_path
            FROM patients
            WHERE patient_id = %s AND user_id = %s;
        """, (patient_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al verificar archivos en la base de datos: {e}")
        return jsonify({'message': 'Error en la base de datos'}), 500

    # Verificar si todas las modalidades tienen un path registrado
    if result and all(result): 
        print("devuelve true") 
        return jsonify({'files_uploaded': True})  # Si todas las modalidades están, responde True
    else:
        print("devuelve FALSE")
        return jsonify({'files_uploaded': False})  # Si falta alguna modalidad, responde False
        
>>>>>>> diegotesis


# Ruta para cargar y procesar archivos de segmentación
@upload.route('/upload-segmentation', methods=['POST'])
def upload_and_process_segmentation():
    # Verificar si los archivos y el patient_id están presentes en la solicitud
    if 'files' not in request.files or 'patient_id' not in request.form:
        response = make_response('No files part or patient ID in the request.', 400)

        # Agregar cabeceras CORS para permitir solicitudes desde otros orígenes
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:4200')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Obtener los archivos y el ID del paciente de la solicitud
    upload_files = request.files.getlist('files')
    patient_id = request.form['patient_id']

    print(f"Files received: {[file.filename for file in upload_files]}")
    print(f"Patient ID received: {patient_id}")

    # Verificar o crear la carpeta donde se guardarán los archivos cargados
    main_path = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(main_path):
        os.makedirs(main_path)

    # Guardar el archivo de segmentación
    for file in upload_files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(main_path, filename))
        print(f"Archivo de segmentación guardado: {filename}")


    # Cargar los archivos de segmentación y procesarlos (similar a las imágenes)
    seg_path = os.path.join(main_path, '*seg.nii.gz')
    seg_list = sorted(glob.glob(seg_path))

    if not seg_list:
        return jsonify({'message': 'Error: No se encontró el archivo de segmentación'}), 400

    print(f"Archivo de segmentación encontrado: {seg_list[0]}")

    # Leer y guardar las segmentaciones
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT t1ce_path, t2_path, flair_path
            FROM patients
            WHERE patient_id = %s;
        """, (patient_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'message': f'Error: No se encontraron registros para el paciente {patient_id}.'}), 404

        t1ce_path = result['t1ce_path']
        t2_path = result['t2_path']
        flair_path = result['flair_path']

        print(f"Paths recuperados de la base de datos:")
        print(f"T1CE Path: {t1ce_path}")
        print(f"T2 Path: {t2_path}")
        print(f"FLAIR Path: {flair_path}")

        if not t1ce_path or not t2_path or not flair_path:
            return jsonify({'message': 'Error: Faltan uno o más paths de modalidades en la base de datos.'}), 400

    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return jsonify({'message': 'Error al consultar la base de datos.'}), 500

    finally:
        cursor.close()
        conn.close()

    # Preprocesar imágenes y segmentaciones
    try:
        temp_image_t1ce = nib.load(t1ce_path).get_fdata()
        temp_image_t2 = nib.load(t2_path).get_fdata()
        temp_image_flair = nib.load(flair_path).get_fdata()
        temp_mask = nib.load(seg_list[0]).get_fdata().astype(np.uint8)

        scaler = MinMaxScaler()
        target_shape = (128, 128, 128)

        # Normalizar imágenes
        temp_image_t1ce = scaler.fit_transform(temp_image_t1ce.reshape(-1, temp_image_t1ce.shape[-1])).reshape(temp_image_t1ce.shape)
        temp_image_t2 = scaler.fit_transform(temp_image_t2.reshape(-1, temp_image_t2.shape[-1])).reshape(temp_image_t2.shape)
        temp_image_flair = scaler.fit_transform(temp_image_flair.reshape(-1, temp_image_flair.shape[-1])).reshape(temp_image_flair.shape)

        # Redimensionar imágenes y segmentaciones
        temp_combined_images = np.stack([temp_image_t1ce, temp_image_t2, temp_image_flair], axis=3)
        temp_combined_images_resized = resize(temp_combined_images, target_shape, mode='constant', anti_aliasing=True)
        temp_mask_resized = resize(temp_mask, target_shape, mode='constant', anti_aliasing=False, preserve_range=True).astype(np.uint8)

        # Codificar segmentaciones
        temp_mask_resized = to_categorical(temp_mask_resized, num_classes=4)

        # Guardar en HDF5
        output_path = 'processed_files/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        h5_filename = os.path.join(output_path, f'{patient_id}_withSeg.h5')
        with h5py.File(h5_filename, 'w') as hf:
            hf.create_dataset('images', data=temp_combined_images_resized, compression='gzip')
            hf.create_dataset('masks', data=temp_mask_resized, compression='gzip')
        print(f"Imágenes y segmentación guardadas para el paciente {patient_id} como HDF5 en {h5_filename}")

    except Exception as e:
        print(f"Error durante el preprocesamiento: {e}")
        return jsonify({'message': f'Error durante el preprocesamiento: {str(e)}'}), 500

    # Verificar si el archivo HDF5 fue creado correctamente
    if os.path.exists(h5_filename):
        return jsonify({
            'message': 'Archivos cargados y procesados exitosamente. Las imágenes y la segmentación han sido guardadas como HDF5.',
            'h5_file': h5_filename
        })
    else:
        return jsonify({'message': f'Error: El archivo HDF5 {h5_filename} no fue creado.'}), 500
