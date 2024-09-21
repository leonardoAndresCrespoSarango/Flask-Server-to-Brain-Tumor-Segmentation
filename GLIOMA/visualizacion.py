
import os
import numpy as np

import nibabel as nib

import matplotlib.pyplot as plt
DATA_TYPES = ['t2w', 't1c', 't1n', 't2f']

def load_data_paths(data_path):
    data_paths = {data_type: [] for data_type in DATA_TYPES}
    for root, dirs, files in os.walk(data_path):
        for file in files:
            for data_type in DATA_TYPES:
                if f'-{data_type}.nii.gz' in file:
                    data_paths[data_type].append(os.path.join(root, file))
    return data_paths

def load_volumes(data_paths):
    volume_paths = [data_paths[data_type][0] for data_type in DATA_TYPES]
    volumes = [nib.load(volume_path).get_fdata() for volume_path in volume_paths]
    volumes = [np.rot90(volume, -1, axes=(0, 1)) for volume in volumes]
    return volumes, volume_paths

def prepare_animation_frames(volumes):
    frames = []
    for i in range(volumes[0].shape[2]):
        frame = np.hstack([volumes[j][:, :, i] for j in range(len(volumes))])
        max_val = np.max(frame)
        if max_val > 0:
            frame = (frame * 255 / max_val).astype(np.uint8)
        else:
            frame = np.zeros_like(frame, dtype=np.uint8)
        frames.append(frame)
    return frames

def add_labels_to_frames(frames, labels):
    labeled_frames = []
    font = plt.matplotlib.font_manager.FontProperties(family='monospace', size=12)
    for frame in frames:
        fig, ax = plt.subplots()
        ax.imshow(frame, cmap='gray')
        for i, label in enumerate(labels):
            ax.text(10 + i * 100, 20, label, color='white', fontproperties=font)
        plt.axis('off')
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        labeled_frames.append(image)
        plt.close(fig)
    return labeled_frames