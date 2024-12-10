import Metashape
import numpy as np
import pandas as pd

def list_coordinates(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')[1:-1]
            # Filter out empty strings before converting to float
            values = [float(val) if val else 0.0 for val in values]
            data.append(tuple(values))
    return data

def process_chunk(chunk, global_coordinates):
    T = chunk.transform.matrix

    data_list = []

    for point_idx, global_coord in enumerate(global_coordinates):
        p = T.inv().mulp(chunk.crs.unproject(Metashape.Vector(global_coord)))
        print(f"Image pixel coordinates of point {point_idx + 1} with global coordinates ({chunk.crs.name}): {global_coord}")

        for i, camera in enumerate(chunk.cameras):
            project_point = camera.project(p)

            if project_point:
                u = project_point.x  # u pixel coordinates in camera
                v = project_point.y  # v pixel coordinates in camera

                if 0 <= u <= camera.sensor.width and 0 <= v <= camera.sensor.height:
                    # Extract video and frame_seq from the camera label
                    camera_label_parts = camera.label.split('_')
                    video = '_'.join(camera_label_parts[:-1])
                    frame_seq = int(camera_label_parts[-1][5:])

                    data_list.append([point_idx + 1, camera.label, video, frame_seq, u, v])

    columns = ['Point', 'Camera', 'video', 'frame_seq', 'u', 'v']
    df = pd.DataFrame(data_list, columns=columns)
    return df

# Define global coordinates for multiple points
points = list_coordinates('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/output/territories_xyz.txt')

# Use active Metashape document
doc = Metashape.app.document

date = '20230302'
session = 'SM_Lek1'
DRONE = ['P1D1', 'P1D2', 'P2D3', 'P2D4', 'P3D5', 'P3D6']

for idx,chunk in enumerate(doc.chunks[2:]):
    print(idx,chunk)
    drone = DRONE[idx]
    
    base_dir = '/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/' + date + '/' + session + '/TalChhapar_' + date + '_' + session + '/output/'
    date_sess_drone = date + '_' + session + '_' + drone

    # Process the current chunk
    df = pd.DataFrame()

    tmp = process_chunk(chunk, points)
    df = pd.concat([df, tmp], ignore_index=True)

    # Save the results to a CSV file
    df.to_csv(base_dir + date_sess_drone + '_territories_uv.csv', index=False)
