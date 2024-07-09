import os
import numpy as np
import nibabel as nib
import glob
import h5py
from skimage.transform import resize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import to_categorical


class ProcessImagesAndCreateHDF5(BaseEstimator, TransformerMixin):
    def __init__(self, target_shape=(128, 128, 128), output_path='./'):
        self.target_shape = target_shape
        self.output_path = output_path
        self.scaler = MinMaxScaler()

    def fit(self, X, y=None):
        return self

    def transform(self, data_folder):
        t1_list = sorted(glob.glob(os.path.join(data_folder, '*/*t1n.nii.gz')))
        t2_list = sorted(glob.glob(os.path.join(data_folder, '*/*t2W.nii.gz')))
        t1ce_list = sorted(glob.glob(os.path.join(data_folder, '*/*t1c.nii.gz')))
        flair_list = sorted(glob.glob(os.path.join(data_folder, '*/*t2f.nii.gz')))
        mask_list = sorted(glob.glob(os.path.join(data_folder, '*/*seg.nii.gz')))

        for img in range(len(t1ce_list)):
            print(f"Now preparing image and masks number: {img}")

            temp_image_t1 = self.load_and_normalize_image(t1_list[img])
            temp_image_t2 = self.load_and_normalize_image(t2_list[img])
            temp_image_t1ce = self.load_and_normalize_image(t1ce_list[img])
            temp_image_flair = self.load_and_normalize_image(flair_list[img])

            temp_mask = nib.load(mask_list[img]).get_fdata().astype(np.uint8)

            temp_combined_images = np.stack([temp_image_t1, temp_image_t2, temp_image_t1ce, temp_image_flair], axis=3)

            temp_combined_images_resized = self.resize_image(temp_combined_images, self.target_shape)
            temp_mask_resized = self.resize_mask(temp_mask, self.target_shape)

            self.save_to_hdf5(temp_combined_images_resized, temp_mask_resized, img)

    def load_and_normalize_image(self, file_path):
        image = nib.load(file_path).get_fdata()
        image = self.scaler.fit_transform(image.reshape(-1, image.shape[-1])).reshape(image.shape)
        return image

    def resize_image(self, image, target_shape):
        return resize(image, target_shape, mode='constant', anti_aliasing=True)

    def resize_mask(self, mask, target_shape):
        mask_resized = resize(mask, target_shape, mode='constant', anti_aliasing=False, preserve_range=True).astype(
            np.uint8)
        return to_categorical(mask_resized, num_classes=4)

    def save_to_hdf5(self, images, masks, patient_id):
        output_file = os.path.join(self.output_path, f'patient_{patient_id}.h5')
        with h5py.File(output_file, 'w') as hf:
            hf.create_dataset('images', data=images, compression='gzip')
            hf.create_dataset('masks', data=masks, compression='gzip')
        print(f"Imagenes y mascaras guardadas con numero de paciente {patient_id} como HDF5")
