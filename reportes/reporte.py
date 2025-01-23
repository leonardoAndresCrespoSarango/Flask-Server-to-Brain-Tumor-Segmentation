from pylatex import Document, Section, Command
from pylatex.utils import NoEscape

def generate_medical_report(patient_id, patient_history, has_cancer, description, doctor_name, doctor_username):
    # Crear documento LaTeX
    doc = Document()
    # Configurar idioma español para el documento
    doc.preamble.append(NoEscape(r'\usepackage[spanish]{babel}'))
    doc.preamble.append(NoEscape(r'\usepackage{datetime}'))
    doc.preamble.append(Command('title', 'Reporte Médico'))
    doc.preamble.append(Command('author', f'{doctor_name} ({doctor_username})'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))  # \today usa el formato del idioma configurado
    doc.append(NoEscape(r'\maketitle'))

    # Información del paciente
    with doc.create(Section('Información del Paciente')):
        doc.append(f'ID del Paciente: {patient_id}\n')
        doc.append(f'Número de Historia Clínica: {patient_history}\n')

    # Diagnóstico médico
    with doc.create(Section('Diagnóstico Médico')):
        doc.append(f'Diagnostico Presuntivo: {"Presenta Cáncer" if has_cancer else "No presenta Cáncer"}\n')
        doc.append(f'Observación del Médico:\n{description}\n')

    # Información del médico
    with doc.create(Section('Médico Responsable')):
        doc.append(f'Nombre del Médico: {doctor_name}\n')
        doc.append(f'Usuario: {doctor_username}\n')

    # Guardar el archivo PDF
    report_path = f'reportes/report_{patient_id}'
    doc.generate_pdf(report_path, clean_tex=True)

    return report_path
