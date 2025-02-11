
import os
import numpy as np

import nibabel as nib

import matplotlib.pyplot as plt
# Definir los tipos de datos de las modalidades de imágenes
DATA_TYPES = ['t2w', 't1c', 't1n', 't2f']

# Función para cargar las rutas de los archivos de datos
#Recorre un directorio dado y busca archivos NIfTI que correspondan a las
#modalidades especificadas en DATA_TYPES. Devuelve un diccionario con
#las rutas de los archivos agrupadas por modalidad.
def load_data_paths(data_path):
    data_paths = {data_type: [] for data_type in DATA_TYPES}

    # Recorrer recursivamente el directorio
    for root, dirs, files in os.walk(data_path):
        for file in files:
            for data_type in DATA_TYPES:
                if f'-{data_type}.nii.gz' in file:
                    data_paths[data_type].append(os.path.join(root, file))
    return data_paths

# Función para cargar los volúmenes de datos
#Carga los volúmenes de imagen para cada modalidad de datos (t2w, t1c, t1n, t2f)
#y los rota según sea necesario para alinear las imágenes.
#Devuelve los volúmenes cargados y las rutas de los archivos.
def load_volumes(data_paths):
    # Tomar la primera ruta de cada modalidad de datos
    volume_paths = [data_paths[data_type][0] for data_type in DATA_TYPES]
    # Cargar los volúmenes y rotarlos
    volumes = [nib.load(volume_path).get_fdata() for volume_path in volume_paths]
    volumes = [np.rot90(volume, -1, axes=(0, 1)) for volume in volumes]
    return volumes, volume_paths

# Función para preparar los cuadros de animación (una por corte de los volúmenes)
#Prepara los cuadros de animación combinando los cortes de las imágenes
#de todas las modalidades en una sola imagen por corte en el eje Z.
#Los cuadros se normalizan a 255 si es necesario.
def prepare_animation_frames(volumes):
    frames = []
    # Iterar sobre los cortes en el eje Z
    for i in range(volumes[0].shape[2]):
        # Combina los cortes de todas las modalidades horizontalmente
        frame = np.hstack([volumes[j][:, :, i] for j in range(len(volumes))])
        max_val = np.max(frame)

        # Normalizar a 255 si el valor máximo es mayor que 0
        if max_val > 0:
            frame = (frame * 255 / max_val).astype(np.uint8)
        else:
            frame = np.zeros_like(frame, dtype=np.uint8)
        frames.append(frame)
    return frames


# Función para agregar etiquetas a los cuadros de animación
#Agrega etiquetas a los cuadros de animación en posiciones fijas.
#Las etiquetas se colocan en la parte superior izquierda de cada cuadro.
def add_labels_to_frames(frames, labels):
    labeled_frames = []
    font = plt.matplotlib.font_manager.FontProperties(family='monospace', size=12)
    for frame in frames:
        # Crear un gráfico y mostrar el cuadro
        fig, ax = plt.subplots()
        ax.imshow(frame, cmap='gray')

        # Añadir etiquetas sobre el cuadro
        for i, label in enumerate(labels):
            ax.text(10 + i * 100, 20, label, color='white', fontproperties=font)
        # Desactivar los ejes
        plt.axis('off')
        fig.canvas.draw()

        # Convertir el gráfico a imagen en formato RGB
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        labeled_frames.append(image)
        # Cerrar la figura para liberar recursos
        plt.close(fig)
    return labeled_frames