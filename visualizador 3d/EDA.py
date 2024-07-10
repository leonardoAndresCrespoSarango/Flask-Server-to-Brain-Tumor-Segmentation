import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting, datasets, surface

hemisphere = 'right'  # Cambiar a 'left' o 'right'
view = 'lateral'  # Cambiar a 'lateral' o 'medial'
colorbar = True
cmap = 'viridis'  # Cambiar a otros mapas de colores disponibles

# Load the surface
fsaverage = datasets.fetch_surf_fsaverage('fsaverage')

# The stat map
stat_img = 'C:/Users/lcres/Desktop/BraTS-GLI-00002-000/BraTS-GLI-00002-000-t1c.nii.gz'

# The texture
texture = surface.vol_to_surf(stat_img, fsaverage.pial_right)

fig = plt.figure(dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Plotting
plotting.plot_surf_roi(fsaverage["infl_{}".format(hemisphere)], roi_map=texture,
                       hemi=hemisphere, view=view, bg_map=fsaverage["sulc_{}".format(hemisphere)],
                       bg_on_data=True, darkness=0.6, output_file='mapped_signal.png',
                       cmap=cmap, colorbar=colorbar, axes=ax, figure=fig)

plotting.show()
plt.close()
