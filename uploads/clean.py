import os
import glob

def clean_uploads_folder():
    """Elimina todos los archivos .nii.gz en la carpeta uploads al iniciar la app."""
    upload_dir = "uploads"  

    # Buscar todos los archivos con extensión .nii.gz
    files_to_delete = glob.glob(os.path.join(upload_dir, "*.nii.gz"))

    # Eliminar cada archivo encontrado
    for file in files_to_delete:
        try:
            os.remove(file)
            #print(f"Eliminado: {file}")
        except Exception as e:
            print(f"Error al eliminar {file}: {e}")

    print("Limpieza de archivos en directorio uploads completada.")
