import Metashape
import numpy as np
import pandas as pd
import os
import sys
import concurrent.futures

def process_camera(camera, df_dict, surface, transform_matrix, chunk):
    """Process a single camera in parallel."""
    data = []
    if camera.label not in df_dict:
        return data  # Skip if camera not in CSV
    
    df_filtered = df_dict[camera.label]
    for _, row in df_filtered.iterrows():
        point, video, frame, u, v = row['Point'], row['video'], row['best_anchor_frame'], row['u'], row['v']
        coords_2D = Metashape.Vector([u, v])

        # Attempt to pick a point on the model surface with jitter
        point_internal = None
        jitter, max_jitter, max_attempts = 0.0001, 1.0, 3

        while point_internal is None and jitter <= max_jitter:
            for _ in range(max_attempts):
                point_internal = surface.pickPoint(camera.center, camera.unproject(coords_2D))
                if point_internal:
                    break
                coords_2D = Metashape.Vector([
                    u + np.random.uniform(-jitter, jitter),
                    v + np.random.uniform(-jitter, jitter)
                ])
            jitter *= 10  # Increase jitter level

        if point_internal is None:
            print(f"Surface model could not be found despite jitters. Camera: {camera.label}, u: {u}, v: {v}")
            continue  # Skip to next point if no projection

        # Transform 3D point to world coordinates
        point3D_world = chunk.crs.project(transform_matrix.mulp(point_internal))

        # Append data
        data.append({
            'Point': point,
            'Camera': camera.label,
            'Video': video,
            'frame': frame,
            'u': u,
            'v': v,
            'x': point3D_world.x,
            'y': point3D_world.y,
            'z': point3D_world.z
        })
    return data

# Main Processing
date = '20230302'
session = 'SM_Lek1'
DRONE = ['P2D4']  # Keep this dynamic for future expansions

doc = Metashape.app.document
chunk = doc.chunks[0]
surface = chunk.model

for idx, chunk in enumerate(doc.chunks[5:6]):  # Keep chunk iteration intact
    print(f"Processing Chunk: {idx}, {chunk.label}")
    drone = DRONE[idx]

    # Define the input/output directory
    base_dir = f'/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/{date}/{session}/{drone}'

    # Get a list of all CSV files in the input directory
    csv_files = [f for f in os.listdir(base_dir) if f.endswith('_Metashape_uv.csv')]

    for csv_file in csv_files:
        csv_path = os.path.join(base_dir, csv_file)
        print(f"Processing file: {csv_file}")

        # Read CSV once, avoid redundant I/O
        df = pd.read_csv(csv_path)

        # Group by camera label for fast lookups
        df_dict = {cam: group for cam, group in df.groupby('Camera')}

        # Cache transformation matrix
        transform_matrix = chunk.transform.matrix

        if not surface:
            raise ValueError("Surface model not found in chunk.")

        # Parallel processing for cameras
        all_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_camera, camera, df_dict, surface, transform_matrix, chunk): camera.label for camera in chunk.cameras}
            for future in concurrent.futures.as_completed(futures):
                all_data.extend(future.result())

        # Convert to DataFrame and save
        df_output = pd.DataFrame(all_data)
        output_csv_path = os.path.join(base_dir, csv_file.replace('_Metashape_uv.csv', '_3D_territories.csv'))
        df_output.to_csv(output_csv_path, index=False)

        print(f"3D world coordinates saved to {output_csv_path}")
        sys.stdout.flush()  # Force flush to console