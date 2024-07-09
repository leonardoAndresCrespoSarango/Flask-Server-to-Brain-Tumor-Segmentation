import numpy as np
import nibabel as nib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.utils import to_categorical
from skimage.transform import resize
from sklearn.base import BaseEstimator, TransformerMixin

class LoadAndNormalizeImages(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scaler = MinMaxScaler()

    def load_and_process_image(self, file_path):
        image = nib.load(file_path).get_fdata()
        image = self.scaler.fit_transform(image.reshape(-1, image.shape[-1])).reshape(image.shape)
        return image

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        t1_path, t2_path, t1ce_path, flair_path = X
        t1 = self.load_and_process_image(t1_path)
        t2 = self.load_and_process_image(t2_path)
        t1ce = self.load_and_process_image(t1ce_path)
        flair = self.load_and_process_image(flair_path)
        return np.stack([t1, t1ce, t2, flair], axis=3)

class ResizeImages(BaseEstimator, TransformerMixin):
    def __init__(self, target_shape=(128, 128, 128)):
        self.target_shape = target_shape

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return resize(X, self.target_shape, mode='constant', anti_aliasing=True)

class ResizeMasks(BaseEstimator, TransformerMixin):
    def __init__(self, target_shape=(128, 128, 128)):
        self.target_shape = target_shape

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        mask = resize(X, self.target_shape, mode='constant', anti_aliasing=False, preserve_range=True).astype(np.uint8)
        return to_categorical(mask, num_classes=4)
