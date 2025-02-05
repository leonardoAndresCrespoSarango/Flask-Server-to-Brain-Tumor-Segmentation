import h5py

#    Carga un archivo HDF5 y extrae el conjunto de imágenes almacenadas en él.
#       :param file_path: Ruta del archivo HDF5 a cargar.
#       :return: Array de imágenes si la carga es exitosa, None en caso de error.

def load_hdf5_file(file_path):
    try:
        with h5py.File(file_path, 'r') as hf:
            images = hf['images'][:]

        return images
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None