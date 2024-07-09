import joblib

data_folder = 'C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/GLIOMA/'

    # Cargar el pipeline
pipeline = joblib.load('image_processing_pipeline.pkl')

    # Usar el pipeline para procesar una nueva carpeta
pipeline.transform(data_folder)
