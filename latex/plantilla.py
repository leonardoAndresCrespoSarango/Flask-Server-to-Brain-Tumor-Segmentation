from pylatex import Document, Section, Subsection, Tabular, MiniPage, LargeText, LineBreak, NewPage, Command, Figure
from pylatex.utils import NoEscape, bold
import subprocess

def create_medical_report(patient_info, diagnosis, mri_images, predictions):
    # Crear documento con opciones de clase
    doc = Document(documentclass='article', document_options=['12pt', 'a4paper'])

    # Título del documento
    doc.preamble.append(Command('title', 'Reporte Médico de Cáncer Cerebral'))
    doc.preamble.append(Command('author', 'Hospital XYZ'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\newpage'))

    # Información del paciente
    with doc.create(Section('Información del Paciente')):
        with doc.create(Tabular('ll')) as table:
            table.add_row((bold('Nombre:'), patient_info['name']))
            table.add_row((bold('Edad:'), patient_info['age']))
            table.add_row((bold('Género:'), patient_info['gender']))
            table.add_row((bold('ID del Paciente:'), patient_info['id']))

    # Diagnóstico
    with doc.create(Section('Diagnóstico')):
        doc.append(diagnosis)

    # Imágenes de Resonancia Magnética
    with doc.create(Section('Imágenes de Resonancia Magnética')):
        for image_path in mri_images:
            with doc.create(Figure(position='h!')) as fig:
                fig.add_image(image_path, width=NoEscape(r'0.8\textwidth'))
                fig.add_caption('Resonancia Magnética')

    # Predicciones del Modelo
    with doc.create(Section('Predicciones del Modelo')):
        for prediction in predictions:
            with doc.create(Subsection(f"Imagen: {prediction['image']}")):
                doc.append(f"Predicción: {prediction['prediction']}")

    # Guardar documento como .tex
    tex_file = 'reporte_medico'
    doc.generate_tex(tex_file)

    # Compilar .tex a .pdf usando pdflatex
    try:
        subprocess.run(['pdflatex', tex_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al compilar el documento: {e}")

# Ejemplo de uso
patient_info = {
    'name': 'Juan Pérez',
    'age': 45,
    'gender': 'Masculino',
    'id': '123456'
}

diagnosis = ("El paciente presenta una masa en el lóbulo frontal izquierdo, "
             "indicativa de un posible glioma. Se recomienda seguimiento y "
             "biopsia para confirmar el diagnóstico.")

mri_images = [
    'C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/tumor.jpg',
    'C:/Users/lcres/PycharmProjects/Flask Server Brain Tumor/tumor.jpg'
]

predictions = [
    {'image': 'tumor 1', 'prediction': 'Positivo para tumor cerebral'},
    {'image': 'tumor 2', 'prediction': 'Negativo para tumor cerebral'}
]

create_medical_report(patient_info, diagnosis, mri_images, predictions)
