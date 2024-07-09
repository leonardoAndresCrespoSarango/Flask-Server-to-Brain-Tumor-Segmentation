import os
import glob
import joblib
from image_processing import ProcessImagesAndCreateHDF5


def create_pipeline(target_shape, output_path):
    return ProcessImagesAndCreateHDF5(target_shape=target_shape, output_path=output_path)


if __name__ == "__main__":
    data_folder = 'C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/GLIOMA/'
    output_path = 'C:/Users/lcres/Desktop/modelo'
    target_shape = (128, 128, 128)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    pipeline = create_pipeline(target_shape, output_path)

    # Guardar el pipeline
    joblib.dump(pipeline, 'image_processing_pipeline.pkl')
