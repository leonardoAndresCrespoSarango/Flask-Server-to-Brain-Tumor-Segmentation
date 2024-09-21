import os
import plotly.graph_objects as go
import plotly.subplots as psub
import numpy as np
from skimage import measure
from datetime import datetime

def generate_graph1(test_img, test_prediction_argmax):
    modalities = ['T1c', 'T2w', 'FLAIR']
    fig = psub.make_subplots(
        rows=2, cols=2,
        subplot_titles=modalities + ['Segmentación Predicha'],
        specs=[[{'type': 'scene'}, {'type': 'scene'}],
               [{'type': 'scene'}, {'type': 'scene'}]],
        horizontal_spacing=0.05,
        vertical_spacing=0.1
    )

    for idx, modality in enumerate(modalities):
        volume = test_img[..., idx]
        verts, faces, normals, values = measure.marching_cubes(volume, level=np.mean(volume), step_size=2)
        fig.add_trace(go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            intensity=values, colorscale='Viridis', opacity=0.3, flatshading=True, name=f'{modality} Brain'
        ), row=idx // 2 + 1, col=idx % 2 + 1)

    full_brain_volume = test_img[..., 0]
    verts, faces, normals, values = measure.marching_cubes(full_brain_volume, level=np.mean(full_brain_volume), step_size=2)
    fig.add_trace(go.Mesh3d(
        x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        intensity=values, colorscale='Viridis', opacity=0.1, flatshading=True, name='Full Brain'
    ), row=2, col=2)

    unique_classes = np.unique(test_prediction_argmax)
    for cls in unique_classes:
        if cls == 0:
            continue
        verts, faces, normals, values = measure.marching_cubes(test_prediction_argmax == cls, level=0.5, step_size=2)
        fig.add_trace(go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            color='red' if cls == 1 else 'green' if cls == 2 else 'blue' if cls == 3 else 'yellow',
            opacity=0.5, flatshading=True, name=f'Segmentación {cls}'
        ), row=2, col=2)

    fig.update_layout(
        title="Visualización cerebral 3D para cada modalidad y segmentación prevista",
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectratio=dict(x=1, y=1, z=1)),
        scene2=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectratio=dict(x=1, y=1, z=1)),
        scene3=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectratio=dict(x=1, y=1, z=1)),
        scene4=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectratio=dict(x=1, y=1, z=1)),
        height=1000, width=1200, margin=dict(l=20, r=20, t=40, b=20)
    )

    graph1_html = f'graph1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph1_html))
    return graph1_html


class_names = {
    1: 'Nucleo Necrotico',
    2: 'Edema',
    3: 'Tumor Activo',

}

def generate_graph2(test_prediction_argmax):
    resolution_mm_per_voxel = 1.0
    class_diameters_voxels = []
    class_diameters_mm = []
    unique_classes = np.unique(test_prediction_argmax)

    # Crear el texto descriptivo para el reporte médico
    report_text = "Reporte de Segmentación Predicha:\n"
    report_text += "Este reporte presenta los diámetros estimados para cada clase de la segmentación predicha en la imagen cerebral.\n"
    report_text += "Las clases se identificaron y midieron utilizando un modelo de predicción.\n\n"
    report_text += "Detalles de los diámetros por clase:\n"

    for cls in unique_classes:
        if cls == 0:
            continue  # Omitir el fondo
        coords = np.argwhere(test_prediction_argmax == cls)
        if coords.size == 0:
            diameter_voxels = 0
            diameter_mm = 0
        else:
            min_coords = coords.min(axis=0)
            max_coords = coords.max(axis=0)
            diameter_voxels = np.linalg.norm(max_coords - min_coords)
            diameter_mm = diameter_voxels * resolution_mm_per_voxel
        class_diameters_voxels.append(diameter_voxels)
        class_diameters_mm.append(diameter_mm)
        class_name = class_names.get(cls, f'Clase {cls}')
        report_text += f"{class_name}: {diameter_mm:.2f} mm\n"

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[class_names.get(cls, f'Clase {cls}') for cls in unique_classes if cls != 0],
        x=class_diameters_mm,
        orientation='h',
        marker=dict(color=['red', 'green', 'blue', 'yellow'][:len(class_diameters_mm)]),
        text=[f'{d:.2f} mm' for d in class_diameters_mm],
        textposition='auto'
    ))

    fig.update_layout(
        title="Diámetros de las Clases en la Segmentación Predicha",
        xaxis_title="Diámetro (en mm)",
        yaxis_title="Clase",
        height=600,
        width=800
    )

    graph2_html = f'graph2_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph2_html))
    return graph2_html, report_text



def generate_graph3(test_img, test_prediction_argmax):
    class_names = ["no Tumor", "Nucleo Necrotico", "Edema", "Nucleo Activo"]

    # Crear una copia de test_prediction_argmax con los nombres de las clases
    test_prediction_named = np.zeros_like(test_prediction_argmax, dtype=object)
    for i, name in enumerate(class_names):
        test_prediction_named[test_prediction_argmax == i] = name

    fig = psub.make_subplots(
        rows=1, cols=2,
        subplot_titles=("MRI Paciente", "Predicción"),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}]]
    )

    fig.add_trace(go.Heatmap(z=test_img[:, :, 0, 1], colorscale='gray', showscale=False, name='MRI Paciente'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=test_prediction_argmax[:, :, 0], showscale=True, colorscale='Viridis', name='Predicción',
                             text=test_prediction_named[:, :, 0], hoverinfo='text'), row=1, col=2)

    frames = []
    for i in range(test_img.shape[2]):
        frame_data = [
            go.Heatmap(z=test_img[:, :, i, 1], colorscale='gray', showscale=False, name='MRI Paciente'),
            go.Heatmap(z=test_prediction_argmax[:, :, i], showscale=True, colorscale='Viridis', name='Predicción',
                       text=test_prediction_named[:, :, i], hoverinfo='text')
        ]
        frames.append(go.Frame(data=frame_data, name=str(i)))

    fig.frames = frames

    steps = []
    for i in range(test_img.shape[2]):
        step = dict(
            method="animate",
            args=[[str(i)], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
            label=str(i)
        )
        steps.append(step)

    sliders = [dict(
        active=0,
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders,
        updatemenus=[dict(type="buttons",
                          showactive=False,
                          buttons=[dict(label="Play",
                                        method="animate",
                                        args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)])])],
        title="Visualización interactiva de sectores",
        height=800,
        width=1200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    graph3_html = f'graph3_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph3_html))
    return graph3_html


def generate_graph4(test_img, test_prediction_argmax):
    class_names = ["no Tumor", "Nucleo Necrotico", "Edema", "Nucleo Activo"]

    # Crear una copia de test_prediction_argmax con los nombres de las clases
    test_prediction_named = np.zeros_like(test_prediction_argmax, dtype=object)
    for i, name in enumerate(class_names):
        test_prediction_named[test_prediction_argmax == i] = name

    # Inicializar la figura con subplots para la imagen de prueba y la segmentación
    fig = psub.make_subplots(
        rows=1, cols=2,
        subplot_titles=("MRI Paciente", "Segmentación"),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}]]
    )

    # Función para generar datos de la imagen en el plano y rebanada seleccionada
    def get_slice(plane, slice_idx):
        if plane == 'Axial':
            img_slice = test_img[:, :, slice_idx, 1]
            seg_slice = test_prediction_argmax[:, :, slice_idx]
            seg_named_slice = test_prediction_named[:, :, slice_idx]
        elif plane == 'Coronal':
            img_slice = test_img[:, slice_idx, :, 1]
            seg_slice = test_prediction_argmax[slice_idx, :, :]
            seg_named_slice = test_prediction_named[slice_idx, :, :]
        elif plane == 'Sagittal':
            img_slice = test_img[slice_idx, :, :, 1]
            seg_slice = test_prediction_argmax[slice_idx, :, :]
            seg_named_slice = test_prediction_named[slice_idx, :, :]
        return img_slice, seg_slice, seg_named_slice

    # Crear datos iniciales para la primera rebanada del plano axial
    img_slice, seg_slice, seg_named_slice = get_slice('Axial', 0)

    # Añadir trazos iniciales a la figura
    fig.add_trace(go.Heatmap(z=img_slice, colorscale='gray', showscale=False, name='MRI Paciente'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=seg_slice, colorscale='Viridis', showscale=True, name='Segmentación',
                             text=seg_named_slice, hoverinfo='text'), row=1, col=2)

    # Crear frames para cada combinación de plano y rebanada
    frames = []
    planes = ['Axial', 'Coronal', 'Sagittal']
    for plane in planes:
        for i in range(test_img.shape[2]):
            img_slice, seg_slice, seg_named_slice = get_slice(plane, i)
            frame_data = [
                go.Heatmap(z=img_slice, colorscale='gray', showscale=False, name='MRI Paciente'),
                go.Heatmap(z=seg_slice, colorscale='Viridis', showscale=True, name='Segmentación',
                           text=seg_named_slice, hoverinfo='text')
            ]
            frames.append(go.Frame(data=frame_data, name=f'{plane}_{i}'))

    fig.frames = frames

    # Crear sliders y botones para la animación y selección de plano/rebanada
    sliders = [dict(
        steps=[
            dict(method='animate', args=[[f'{plane}_{i}'], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))], label=f'{plane} - Slice {i}')
            for plane in planes for i in range(test_img.shape[2])
        ],
        currentvalue=dict(prefix='Rebanada: ')
    )]

    fig.update_layout(
        sliders=sliders,
        updatemenus=[dict(type='buttons', showactive=False, buttons=[dict(label='Play', method='animate', args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)])])],
        title="Visualización interactiva de cortes cerebrales",
        height=800,
        width=1200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white'
    )

    graph4_html = f'graph4_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph4_html))
    return graph4_html
def generate_graph5(test_img, test_prediction_argmax):
    # Crear la gráfica fija que muestra las clases presentes en cada slice
    classes_per_slice = []
    num_classes_per_slice = []
    class_names = ["no Tumor", "Nucleo Necrotico", "Edema", "Nucleo Activo"]
    for i in range(test_img.shape[2]):
        unique_classes = np.unique(test_prediction_argmax[:, :, i])
        relevant_classes = [class_names[c] for c in unique_classes if c != 0]
        classes_per_slice.append(relevant_classes)
        num_classes_per_slice.append(len(relevant_classes))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(test_img.shape[2])),
        y=num_classes_per_slice,
        mode='lines+markers',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Presencia de clase en cada segmentación",
        xaxis_title="Número de rebanada",
        yaxis_title="Número de clases",
        height=600,
        width=800
    )

    graph5_html = f'graph5_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph5_html))

    # Crear el texto descriptivo para el reporte médico
    report_text5 = "Reporte de Segmentación Predicha:\n"
    report_text5 += "Este reporte presenta las clases presentes en cada rebanada de la segmentación predicha.\n\n"
    report_text5 += "Resumen de las clases presentes por rebanada (omitiendo 'no Tumor'):\n"

    def summarize_slices(classes_per_slice):
        summary = []
        start = 0
        current_classes = classes_per_slice[0]

        for i in range(1, len(classes_per_slice)):
            if classes_per_slice[i] != current_classes:
                if current_classes:
                    summary.append((start, i - 1, current_classes))
                start = i
                current_classes = classes_per_slice[i]

        if current_classes:
            summary.append((start, len(classes_per_slice) - 1, current_classes))

        return summary

    slice_summary = summarize_slices(classes_per_slice)
    for start, end, classes in slice_summary:
        if start == end:
            report_text5 += f"Rebanada {start}: {', '.join(classes)}\n"
        else:
            report_text5 += f"Rebanadas {start} - {end}: {', '.join(classes)}\n"

    return graph5_html, report_text5
# Función para generar la sexta gráfica
def generate_graph6(test_img, test_prediction_argmax):
    class_names = ["no Tumor", "Nucleo Necrotico", "Edema", "Nucleo Activo"]
    modalities = ['T1c', 'T2w', 'FLAIR']
    modality_index = {modality: i for i, modality in enumerate(modalities)}

    # Crear una copia de test_prediction_argmax con los nombres de las clases
    test_prediction_named = np.zeros_like(test_prediction_argmax, dtype=object)
    for i, name in enumerate(class_names):
        test_prediction_named[test_prediction_argmax == i] = name

    # Crear la figura inicial con dos subplots
    fig = psub.make_subplots(
        rows=1, cols=2,
        subplot_titles=("MRI Paciente", "Predicción del paciente"),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}]]
    )

    # Añadir trazas iniciales (modalidad T1c y primer slice por defecto)
    fig.add_trace(go.Heatmap(z=test_img[:, :, 0, modality_index['T1c']], colorscale='gray', showscale=False), row=1, col=1)
    fig.add_trace(go.Heatmap(z=test_prediction_argmax[:, :, 0], showscale=True, colorscale='Viridis',
                             text=test_prediction_named[:, :, 0], hoverinfo='text'), row=1, col=2)

    # Crear los frames para todas las combinaciones de modalidad y slice
    frames = []
    for modality in modalities:
        for slice_index in range(test_img.shape[2]):
            frames.append(go.Frame(
                data=[
                    go.Heatmap(z=test_img[:, :, slice_index, modality_index[modality]], colorscale='gray', showscale=False),
                    go.Heatmap(z=test_prediction_argmax[:, :, slice_index], showscale=True, colorscale='Viridis',
                               text=test_prediction_named[:, :, slice_index], hoverinfo='text')
                ],
                name=f"{modality}_{slice_index}"
            ))

    # Añadir los frames a la figura
    fig.frames = frames

    # Crear el slider
    steps = []
    for slice_index in range(test_img.shape[2]):
        step = dict(
            method="animate",
            args=[[f"{modalities[0]}_{slice_index}"], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
            label=str(slice_index)
        )
        steps.append(step)

    sliders = [dict(
        active=0,
        pad={"t": 50},
        steps=steps
    )]

    # Crear el menú de botones para seleccionar la modalidad
    updatemenus = [
        dict(
            buttons=[
                dict(label=modality, method='animate',
                     args=[[f"{modality}_{slice_index}" for slice_index in range(test_img.shape[2])],
                           dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))])
                for modality in modalities
            ],
            direction='down',
            showactive=True,
            x=0.5,
            xanchor='left',
            y=1.2,
            yanchor='top'
        )
    ]

    # Actualizar el layout de la figura
    fig.update_layout(
        sliders=sliders,
        updatemenus=updatemenus,
        title="Visualización interactiva de rebanadas",
        height=800,
        width=1200,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        yaxis2=dict(showgrid=False),
    )

    graph6_html = f'graph6_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    fig.write_html(os.path.join('static', graph6_html))
    return graph6_html