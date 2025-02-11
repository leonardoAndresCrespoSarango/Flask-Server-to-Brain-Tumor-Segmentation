<p align="center">
  <img src="https://github.com/CarlosSaico28/Anscombe/assets/84851722/8df0a848-a06e-46ff-b27c-944650b0fbe1" alt="company_logo">
</p>


**Ingeniería en Ciencias de la Computación**
<h1 align="center">Servidor Flask para Predicción de Segmentación de Tumores Cerebrales</h1>

<p align="justify">
Este proyecto implementa un servidor web basado en Flask para la segmentación de tumores cerebrales en imágenes de resonancia magnética (MRI).  
Utiliza un modelo de deep learning U-Net previamente entrenado para detectar y segmentar regiones tumorales en las modalidades: T1C, T2W y T2F.  

La aplicación permite a los usuarios cargar imágenes médicas en formato NIfTI (.nii.gz), procesarlas y obtener una predicción en tiempo real.  
Además, proporciona una API REST que facilita la integración con el FrontEnd para consumir los endpoints.

Este servidor es una herramienta útil para la investigación en neuroimagen, ayudando a médicos y científicos en la detección automatizada de tumores cerebrales.
</p>

<h2 align="justify"><strong>Librerias Necesarias</strong></h2>

- Las librerias se encuentran en el archivo **requirements.txt**, para instalarlas ejecutamos en la terminal el comando **pip install -r requirements.txt**

<h2 align="justify"><strong>Herramientas Adicionales</strong></h2>

<p align="justify">Se debe instalar MiKTeX y Strawberry Perl ya que se utilizan para generar los reportes en LaTeX, especialmente para la gestión de bibliografía con biber.</p>

- <strong>MiKTeX:</strong> Distribución de LaTeX para generar reportes y documentación científica. 

- <strong>Strawberry Perl:</strong> Requerido para ejecutar `biber`, utilizado en la gestión de bibliografía en LaTeX.  


<p align="center" style="font-size: 1px;">
</p>
<h2 align="justify"><strong>Estructura del Proyecto</strong></h2>

📂 Flask-Server-to-Brain-Tumor-Segmentation<br>
│── 📄 app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Servidor Flask principal<br>
│── 📄 DataBase.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Gestión de base de datos<br>
│── 📄 estructura.txt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Descripción de la estructura del proyecto<br>
│── 📄 H5.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Manejo de archivos H5<br>
│── 📄 README.md &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Documentación del proyecto<br>
│── 📄 requirements.txt &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Dependencias necesarias<br>
│── 📄 UNET.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Modelo UNET para segmentación<br>
├── 📂 Artificial_Intelligence_Brats/  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Funcionalidades de IA<br>
│   ├── 📂 AI_BraTs_Function_predict/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 prediction.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 predictionAI.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📂 AI_BraTs_Function_report/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 report.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📂 AI_BraTs_Function_result/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 result.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📂 AI_BraTs_Function_upload_N_ProcessFile/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 upload_and_process_files.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 diagnostic/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Funcionalidades de diagnóstico<br>
│   ├── 📄 diagnostic.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 diagnostic_with_patient.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 GLIOMA/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Visualización de pacientes<br>
│   ├── 📄 animation.gif &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 paciente.ipynb &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 vializador.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 visualizacion.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 graficas/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Generación de gráficos<br>
│   ├── 📄 graficasPloty.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 latex/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Generación de reportes en LaTeX<br>
│   ├── 📄 plantilla.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 model_3D/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Modelos en 3D<br>
│   ├── 📂 3 clases/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   └── 📄 modelUnet3D_3.h5 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 patient/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Manejo de datos de pacientes<br>
│   ├── 📄 patient.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # También se agregó los histogramas<br>
│<br>
├── 📂 processed_files/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Archivos procesados<br>
│<br>
├── 📂 reportes/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Reportes generados<br>
│   ├── 📄 reporte.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 report_*.pdf &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Reportes en formato PDF<br>
│   ├── 📄 report_*.tex &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Reportes en formato LaTeX<br>
│<br>
├── 📂 reports/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Funciones para generar reportes<br>
│   ├── 📄 reportePDF.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 routes/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Rutas del servidor Flask<br>
│   ├── 📄 login.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 predictionsMedia.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 routes.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Envío de la encuesta<br>
│   ├── 📄 user.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 static/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Archivos estáticos (imágenes, CSS, JS)<br>
│   ├── 📂 images/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 graph2.png &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   │   ├── 📄 graph5.png &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 templates/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Plantillas HTML para la interfaz web<br>
│   ├── 📄 index.html &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 result.html &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│<br>
├── 📂 uploads/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Archivos subidos por los usuarios<br>
│   ├── 📄 Modelos H5, imágenes NIfTI, etc.<br>
│<br>
├── 📂 visualizador 3D/ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; # Scripts para visualización en 3D<br>
│   ├── 📄 EDA.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>
│   ├── 📄 mapped_signal.png &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>

