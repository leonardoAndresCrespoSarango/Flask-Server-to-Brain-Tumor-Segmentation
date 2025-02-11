import os
from pylatex import Document, Section, Tabular, Command, Figure, Package
from pylatex.utils import NoEscape, bold
import subprocess

#Crea un informe médico en formato PDF utilizando LaTeX.
#Incluye información del paciente, predicción, diagnóstico y las imágenes de resonancia magnética.
def create_medical_report(patient_info, prediagnosis, mri_images, report_filename):
    # Crear un documento de LaTeX con las configuraciones necesarias
    doc = Document(documentclass='article', document_options=['12pt', 'a4paper'])

    # Importar el paquete float para usar la opción H
    doc.packages.append(Package('float'))

    # Añadir el título, autor y fecha al documento
    doc.preamble.append(Command('title', 'Reporte Médico de Cáncer Cerebral'))
    doc.preamble.append(Command('author', 'Hospital XYZ'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))
    doc.append(NoEscape(r'\newpage'))

    # Sección con la información del paciente
    with doc.create(Section('Información del Paciente')):
        with doc.create(Tabular('ll')) as table:
            table.add_row((bold('Nombre:'), patient_info['name']))
            table.add_row((bold('Edad:'), patient_info['age']))
            table.add_row((bold('Género:'), patient_info['gender']))
            table.add_row((bold('ID del Paciente:'), patient_info['id']))

    # Sección con el prediagnóstico
    with doc.create(Section('Prediagnóstico')):
        doc.append(prediagnosis)

    # Sección con el diagnóstico
    with doc.create(Section('Diagnóstico')):
        doc.append("Diagnóstico basado en las predicciones.")

    # Sección con las imágenes de resonancia magnética
    with doc.create(Section('Imágenes de Resonancia Magnética')):
        for image_path in mri_images:
            image_num = int(image_path.split('_')[-1].split('.')[0])
            if 40 <= image_num <= 100:
                with doc.create(Figure(position='H')) as fig:
                    fig.add_image(image_path, width=NoEscape(r'0.8\textwidth'))
                    fig.add_caption(f'Resonancia Magnética - Slice {image_num}')

    # Crear el archivo .tex y generar el PDF
    tex_file = report_filename.replace('.pdf', '')  # Remover la extensión para el archivo .tex
    doc.generate_tex(tex_file)

    try:
        # Ejecutar el compilador pdflatex para generar el PDF
        subprocess.run(['pdflatex', tex_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al compilar el documento: {e}")

    # Borrar las imágenes temporales después de generar el informe
    for image_path in mri_images:
        try:
            os.remove(image_path)
        except Exception as e:
            print(f"Error al borrar la imagen temporal {image_path}: {e}")
