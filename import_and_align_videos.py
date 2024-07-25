import Metashape
import datetime
import glob
import os
import pathlib
import numpy as np
import helper_functions as hf

# The directories where videos are saved
VideoDirectories = [
    "/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/videos/P1D1/",
    "/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/videos/P1D2/"
]

# The directory where frames must be imported
ImageDirectory = "/Volumes/EAS_shared/blackbuck/working/rawdata/Field_Recording_2023/Original/SSD7/20230316/SE_Lek1/P1_Images/"

def list_videos(directory):
    directory_path = pathlib.Path(directory)
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
    
    video_files = []
    for file in directory_path.iterdir():
        if not file.name.startswith('.') and file.suffix.lower() in video_extensions:
            video_files.append((str(file.resolve()), file.stem))
    
    return video_files

def import_frames(video_path, video_name, import_directory):
    # Create a folder for each video
    video_folder = os.path.join(import_directory, video_name)
    os.makedirs(video_folder, exist_ok=True)

    # Define the image names pattern for frames
    image_names = os.path.join(video_folder, f'{video_name}_{{filenum:04}}.png')

    # Import frames with custom frame step
    chunk.importVideo(video_path, image_names, frame_step=Metashape.FrameStep.CustomFrameStep, custom_frame_step=300)

# Load current metashape document and assign the active chunk as reference
doc = Metashape.app.document

hf.log( "--- Starting workflow ---" )
hf.log( "Metashape version " + Metashape.app.version )
hf.log_time()

# Collect videos from all directories
all_videos = []
for video_dir in VideoDirectories:
    all_videos.extend(list_videos(video_dir))

# Check if any videos found
if not all_videos:
    hf.log("No videos found in the directories.")
else:
    # Create a single chunk for listed videos
    chunk = doc.addChunk()
    chunk.label = all_videos[0][1][:19]

    # Import frames from listed videos
    for video_path, video_name in all_videos:
        import_frames(video_path, video_name, ImageDirectory)


# Parameters for feature matching photos
match_photos_config = {
    'downscale': 1,
    'generic_preselection': True,
    'reference_preselection': True,
    'reference_preselection_mode': Metashape.ReferencePreselectionSource,
    'keypoint_limit': 40000,
    'tiepoint_limit': 4000
}

# Match photos and align cameras in chunk
hf.log( "Processing chunk" )
print(chunk.label)

chunk.matchPhotos(**match_photos_config)
chunk.alignCameras()

hf.log_time()
hf.log( "--- Finished workflow ---")

# doc.save('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/TalChhapar/TalChhapar_Test.psx')
