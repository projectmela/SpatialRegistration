import Metashape
import numpy as np
import pandas as pd
import os

date = '20230302'
session = 'SM_Lek1'
DRONE = ['P1D1']#, 'P1D2', 'P2D3', 'P2D4', 'P3D5', 'P3D6']

# Load the Metashape document and access the first chunk and its surface model
doc = Metashape.app.document
chunk = doc.chunks[0]
surface = chunk.model

# Ensure surface model exists
if not surface:
    raise ValueError("Surface model not found in chunk.")

for idx,chunk in enumerate(doc.chunks[2:3]):
    print(f"Processing Chunk: {idx, chunk.label}")
    drone = DRONE[idx]

    # Define the input/output directory
    base_dir = '/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/' + date + '/' + session + '/' + drone

    # Get a list of all CSV files in the input directory
    csv_files = [f for f in os.listdir(base_dir) if f.endswith('_Metashape_uv.csv')]

    # Process each CSV file
    for csv_file in csv_files:
        csv_path = os.path.join(base_dir, csv_file)
        print(f"Processing file: {csv_file}")

        # Read the CSV file
        df = pd.read_csv(csv_path)
        data = []

        # Iterate through cameras in the chunk
        for camera in chunk.cameras:

            # Filter the DataFrame to only include rows related to a specific camera
            df_filtered = df[df['Camera'] == camera.label]
              
            # Iterate through the filtered DataFrame and process each point
            for index, row in df_filtered.iterrows():
                point = row['Point']
                camera_label = row['Camera']
                video = row['video']
                frame = row['best_anchor_frame']
                u = row['u']
                v = row['v']

                # Create a 2D vector from the coordinates
                coords_2D = Metashape.Vector([u, v])
                  
                # Attempt to pick a point on the model surface with jitter if necessary
                point_internal = None
                jitter = 0.0001
                max_jitter = 1.0  # Set a reasonable upper limit for jitter

                while point_internal is None and jitter <= max_jitter:
                    attempts = 0
                    while point_internal is None and attempts < 5:
                        point_internal = surface.pickPoint(camera.center, camera.unproject(coords_2D))
                        if point_internal is None:
                            u_jittered = u + np.random.uniform(-jitter, jitter)
                            v_jittered = v + np.random.uniform(-jitter, jitter)
                            coords_2D = Metashape.Vector([u_jittered, v_jittered])
                            attempts += 1
                            print(f"Jitter used: {jitter}, Camera: {camera_label}, u: {u_jittered}, v: {v_jittered}")

                    if point_internal is None:
                        jitter *= 10  # Increase jitter for the next iteration

                if point_internal is None:
                    print(f"Surface model could not be found despite several jitters. Camera: {camera_label}, u: {u}, v: {v}")
                    continue  # Skip to the next iteration if the point could not be picked
                  
                # Transform the internal 3D point to world coordinates
                point3D_world = chunk.crs.project(chunk.transform.matrix.mulp(point_internal))

                # Append the data to the list
                data.append({
                    'Point': point,
                    'Camera': camera_label,
                    'Video': video,
                    'frame': frame,
                    'u': u,
                    'v': v,
                    'x': point3D_world.x,
                    'y': point3D_world.y,
                    'z': point3D_world.z
                })
    
        # Convert the list to a DataFrame
        df_output = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        output_csv_path = base_dir + '/' + csv_file[:-17] + '_3D_territories.csv'
        df_output.to_csv(output_csv_path, index=False)

        print(f"3D world coordinates saved to {output_csv_path}")