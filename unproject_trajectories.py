import Metashape
import pandas as pd
import numpy as np

# Load the Metashape document and access the first chunk and its surface model
doc = Metashape.app.document
chunk = doc.chunks[0]
surface = chunk.model

# Switch to a different chunk for processing
chunk = doc.chunks[2]
print(f"Processing Chunk: {chunk.label}")

# Read the CSV file into a DataFrame
csv_path = '/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/output/trajectories_uv.csv'
df = pd.read_csv(csv_path)

# Initialize an empty list to store the data
data = []

# Iterate through cameras in the chunk
for camera in chunk.cameras:

    # Filter the DataFrame to only include rows related to a specific camera
    df_filtered = df[df['Camera'] == camera.label]
    
    # Iterate through the filtered DataFrame and process each point
    for index, row in df_filtered.iterrows():
        idx = row['idx']
        camera_label = row['Camera']
        frame = row['frame']
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
            'idx': idx,
            'Camera': camera_label,
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
output_csv_path = '/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/output/trajectories_3D_world.csv'
df_output.to_csv(output_csv_path, index=False)

print(f"3D world coordinates saved to {output_csv_path}")
