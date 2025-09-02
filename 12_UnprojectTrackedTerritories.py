import Metashape
import numpy as np
import pandas as pd
import os
import glob
import concurrent.futures
import time

def process_camera(camera, df_dict, surface, transform_matrix, chunk):
    """Process a single camera in parallel."""
    start_time = time.time()
    data = []

    if camera.label not in df_dict:
        print(f"[DEBUG] Camera '{camera.label}' not found in CSV. Skipping.")
        return data  # Skip if camera not in CSV
    
    df_filtered = df_dict[camera.label]
    skipped_points = 0
    processed_points = 0

    for _, row in df_filtered.iterrows():
        point, video, frame, u, v = row['Point'], row['video'], row['best_anchor_frame'], row['u'], row['v']
        coords_2D = Metashape.Vector([u, v])

        # Attempt to pick a point on the model surface with jitter
        point_internal = None
        jitter, max_jitter, max_attempts = 0.0001, 0.1, 3

        while point_internal is None and jitter <= max_jitter:
            for _ in range(max_attempts):
                coords_3D = camera.unproject(coords_2D)
                print(f"Camera: {camera.label}, u: {u}, v: {v}, Unprojected 3D: {coords_3D}")
                
                point_internal = surface.pickPoint(camera.center, coords_3D)
                if point_internal:
                    break
                coords_2D = Metashape.Vector([
                    u + np.random.uniform(-jitter, jitter),
                    v + np.random.uniform(-jitter, jitter)
                ])
            jitter *= 10  # Increase jitter level

        if point_internal is None:
            print(f"Surface model could not be found despite jitters. Camera: {camera.label}, u: {u}, v: {v}")
            skipped_points += 1
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
            'latitude': point3D_world.y,
            'longitude': point3D_world.x,
            'altitude': point3D_world.z
        })
        processed_points += 1

    return data

# Main Processing
date = '20230318'
session = 'SM_Lek1'
DRONE = ['P3D5']#, 'P1D2', 'P2D3', 'P2D4', 'P3D5', 'P3D6']

doc = Metashape.app.document
chunk = doc.chunks[0]
surface = chunk.model

for drone in DRONE:
    # Define the input/output directory
    base_dir = f'/Volumes/SSD5/{date}/{session}/{drone}'

    # Get a sorted list of CSV files using glob
    csv_files = sorted(glob.glob(os.path.join(base_dir, '*_Metashape_uv.csv')))

    for csv_file in csv_files:
        csv_path = os.path.join(base_dir, csv_file)
        print(f"Processing file: {csv_file}")

        df = pd.read_csv(csv_path)

        # Group by camera label for fast lookups
        df_dict = {cam: group for cam, group in df.groupby('Camera')}

        # Cache transformation matrix
        transform_matrix = chunk.transform.matrix

        if not surface:
            raise ValueError("Surface model not found in chunk.")

        # Filter Cameras** (Keep only those with 7 label parts)
        valid_cameras = [
            camera for camera in chunk.cameras
            if len(camera.label.split('_')) == 7 and camera.label.split('_')[3] == drone
        ]

        # Parallel processing for cameras
        all_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_camera, camera, df_dict, surface, transform_matrix, chunk): camera.label for camera in valid_cameras}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    all_data.extend(result)

        if not all_data:
            print(f"[ERROR] No valid 3D world coordinates generated for {csv_file}. Check camera matching and surface model.")

        # Convert to DataFrame and save
        df_output = pd.DataFrame(all_data)
        output_csv_path = os.path.join(base_dir, csv_file.replace('_Metashape_uv.csv', '_3D_territories.csv'))
        df_output.to_csv(output_csv_path, index=False)

        print(f"3D world coordinates saved to {output_csv_path}")