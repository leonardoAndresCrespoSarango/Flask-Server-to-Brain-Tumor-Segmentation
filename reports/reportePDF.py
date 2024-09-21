from fpdf import FPDF
class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Reporte Médico Generado por IA', 0, 1, 'C')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_patient_info(self, patient_id):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Datos del Paciente', 0, 1, 'L')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f"ID del Paciente: {patient_id}", 0, 1)
        self.ln(10)

    def add_modalities_description(self):
        description = (
            "1. T1c (T1-weighted contrast-enhanced imaging): Esta modalidad se utiliza para resaltar estructuras "
            "anatómicas y anormalidades en el cerebro. La administración de un agente de contraste mejora la visualización "
            "de lesiones como tumores, inflamaciones y áreas de ruptura de la barrera hematoencefálica.\n\n"
            "2. T2w (T2-weighted imaging): Esta modalidad se utiliza para resaltar diferencias en el contenido de agua de "
            "los tejidos cerebrales. Es útil para identificar lesiones que contienen líquido, como edemas, inflamaciones y "
            "algunos tipos de tumores.\n\n"
            "3. FLAIR (Fluid-Attenuated Inversion Recovery): Esta modalidad es una variación de la imagen ponderada en T2 "
            "que suprime el líquido cefalorraquídeo, permitiendo una mejor visualización de lesiones cerca de los ventrículos "
            "cerebrales y otras áreas de alto contenido de agua."
        )
        self.chapter_title('Descripción de Modalidades (T1c, T2w, FLAIR)')
        self.chapter_body(description)

    def format_feedback(self, feedback):
        formatted_feedback = (
            f"Precisión de la IA: {'Sí' if feedback['iaAccuracy'] == 'si' else 'No' if feedback['iaAccuracy'] == 'no' else 'Parcialmente'}\n"
            f"Utilidad de la IA: {'Muy útil' if feedback['iaUsefulness'] == 'muy_util' else 'Útil' if feedback['iaUsefulness'] == 'util' else 'Poco útil' if feedback['iaUsefulness'] == 'poco_util' else 'Inútil'}\n"
            f"Identificación de Regiones: {'Sí' if feedback['iaRegions'] == 'si' else 'No' if feedback['iaRegions'] == 'no' else 'Parcialmente'}\n"
            f"Comparación con otros métodos: {feedback['iaComparison']}\n"
            f"Confiabilidad de la IA: {'Muy confiable' if feedback['iaReliability'] == 'muy_confiable' else 'Confiable' if feedback['iaReliability'] == 'confiable' else 'Poco confiable' if feedback['iaReliability'] == 'poco_confiable' else 'Inconfiable'}\n"
            f"Comentarios adicionales: {feedback['additionalComments']}\n"
            f"Descripción de las modalidades: {feedback['modalitiesDescription']}"
        )
        return formatted_feedback