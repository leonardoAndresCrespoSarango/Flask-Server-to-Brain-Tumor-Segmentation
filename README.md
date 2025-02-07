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
│── 📂 models/              # Modelos de deep learning<br>
│── 📂 static/              # Archivos estáticos (si aplica)<br>
│── 📂 templates/           # Interfaz web (si aplica)<br>
│── app.py                  # Servidor Flask<br>
│── requirements.txt         # Dependencias<br>
│── README.md                # Documentación<br>
