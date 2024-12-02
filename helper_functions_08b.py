import Metashape
import datetime
import glob
import os
import pathlib


# Helper functions

def log(msg):
    print(msg)


def log_time():
    log( datetime.datetime.now() )


def make_project_filename(project_dir, ext):
    'Make a filename in the project directory with the given extension'
    dir_name = os.path.basename(project_dir)
    return os.path.join(project_dir,dir_name + "." + ext);


def get_subdirectories(parent_dir, ignore_files=None):
    'Find all the folders in the parent_dir and its subdirectories'
    if ignore_files is None:
        ignore_files = []

    subdirs = [os.path.join(parent_dir, d) for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d))]
    
    result_subdirs = []
    for subdir in subdirs:
        files_in_subdir = [f for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f)) and f not in ignore_files]
        if files_in_subdir:
            result_subdirs.append(subdir)
        result_subdirs.extend(get_subdirectories(subdir, ignore_files))

    return result_subdirs


def make_project(project_dir, chunk_dirs):
    'Make a new project and a chunk for each directory.'

    log( "Making project " + project_dir )

    # Create new doc
    doc = Metashape.Document() # Operate on a new document for batch proecssing
    #doc = Metashape.app.document # Use the current open document in Metashape

    # Go through each chunk directory
    for chunk_dir in chunk_dirs:
        chunk = doc.addChunk() # Create the chunk
        chunk.label = os.path.basename(chunk_dir)
        photos = os.listdir(chunk_dir) # Get the photos filenames
        photos = [os.path.join(chunk_dir,p) for p in photos] # Make them into a full path
        log( "Found {} photos in {}".format(len(photos), chunk_dir))
        if not chunk.addPhotos(photos):
            log( "ERROR: Failed to add photos: " + str(photos))

    # Save the new project
    project_name = make_project_filename(project_dir, "psz")
    log( "Saving: " + project_name );
    if not doc.save( project_name ):
        log( "ERROR: Failed to save project: " + project_name)

    return doc