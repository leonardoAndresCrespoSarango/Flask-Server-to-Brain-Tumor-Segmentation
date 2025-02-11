import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting, datasets, surface


# Definimos la hemisferio y la vista para la visualización
hemisphere = 'right'  # Cambiar a 'left' o 'right'
view = 'lateral'  # Cambiar a 'lateral' o 'medial'
colorbar = True
cmap = 'viridis'  # Cambiar a otros mapas de colores disponibles

# Cargar el conjunto de datos de la superficie fsaverage
fsaverage = datasets.fetch_surf_fsaverage('fsaverage')

# Ruta del archivo de imagen estadística (mapa de actividad)
stat_img = 'C:/Users/lcres/Desktop/BraTS-GLI-00002-000/BraTS-GLI-00002-000-t1c.nii.gz'

# Convertir la imagen volumétrica a la superficie
# Esto asocia la imagen de actividad con la superficie de la corteza cerebral
texture = surface.vol_to_surf(stat_img, fsaverage.pial_right)

# Crear la figura para la visualización
fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Realizamos la visualización
# La función `plot_surf_roi` visualiza el mapa de la región de interés (ROI) sobre la superficie cerebral
plotting.plot_surf_roi(fsaverage["infl_{}".format(hemisphere)], roi_map=texture,
                       hemi=hemisphere, view=view, bg_map=fsaverage["sulc_{}".format(hemisphere)],
                       bg_on_data=True, darkness=0.6, output_file='mapped_signal.png',
                       cmap=cmap, colorbar=colorbar, axes=ax, figure=fig)

# Mostrar la visualización
plotting.show()
# Cerrar la figura para liberar recursos después de mostrarla
plt.close()
