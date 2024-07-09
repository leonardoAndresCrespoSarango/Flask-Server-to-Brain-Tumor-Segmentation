import h5py


def load_hdf5_file(file_path):
    try:
        with h5py.File(file_path, 'r') as hf:
            images = hf['images'][:]
            masks = hf['masks'][:]
        return images, masks
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None, None