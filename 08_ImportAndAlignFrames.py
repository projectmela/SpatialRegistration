import Metashape
import datetime
import glob
import os
import pathlib
import numpy as np
import helper_functions_08b as hf

# The directories where videos are saved
ImagesDirectory = [
    "/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/20230302/SM_Lek1/P1D1/",
    "/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/20230302/SM_Lek1/P2D3/",
    "/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/20230302/SM_Lek1/P3D5/"
]

import pathlib

def list_image_folders(directory):
    directory_path = pathlib.Path(directory)

    # List all subdirectories
    folder_names = [folder.name for folder in directory_path.iterdir() if folder.is_dir() and not folder.name.startswith('.')]
    
    return folder_names

def import_frames(import_directory):
    # Get a list of all image files in the folder
    image_extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']  # Supported image formats
    image_files = [os.path.join(import_directory, f) for f in os.listdir(import_directory)
                   if os.path.splitext(f)[1].lower() in image_extensions]

    # Ensure the folder contains images
    if not image_files:
        raise FileNotFoundError(f"No image files found in directory: {import_directory}")

    # Import images into the chunk
    chunk.addPhotos(image_files)

    print(f"Successfully imported {len(image_files)} images from {import_directory} into the chunk.")



# Load current metashape document and assign the active chunk as reference
doc = Metashape.app.document

hf.log( "--- Starting workflow ---" )
hf.log( "Metashape version " + Metashape.app.version )
hf.log_time()

# Collect videos from all directories
all_folders = []
for image_dir in ImagesDirectory:
    all_folders.extend(list_image_folders(image_dir))

    print(all_folders)

for idx,label in enumerate(all_folders):
    # Check if any videos found
    if not all_folders:
        hf.log("No folders found in the parent directory.")
    else:
        # Create a single chunk for listed videos
        chunk = doc.addChunk()
        chunk.label = label

        # Import frames from current folder
        current_dir = ImagesDirectory[idx] + label
        import_frames(current_dir)

        # Parameters for feature matching photos
        match_photos_config = {
            'downscale': 1,
            'generic_preselection': True,
            'reference_preselection': True,
            'reference_preselection_mode': Metashape.ReferencePreselectionSource,
            'keypoint_limit': 40000,
            'tiepoint_limit': 10000
        }

        # Match photos and align cameras in chunk
        hf.log( "Processing chunk" )
        print(chunk.label)

        chunk.matchPhotos(**match_photos_config)
        chunk.alignCameras()

hf.log_time()
hf.log( "--- Finished workflow ---")

# doc.save('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/TalChhapar_Test.psx')
