import os
import glob
import pandas as pd
import cv2

# Worker function to process a single (date, session, drone)
def process_task(task):
    date, session, drone, files_directory, video_directory = task
    print(date, session, drone)

    files_path = f"{files_directory}/{date}/{session}/{drone}"
    video_path = f"{video_directory}/{date}/{session}/{drone}"
    
    files = glob.glob(f"{files_path}/{date}_{session}_{drone}*_Anchored.csv")

    for file in sorted(files):
        df = pd.read_csv(file).dropna()
        df['best_anchor_frame'] = df['best_anchor_frame'].astype(int)

        # Step 1: Extract unique frame numbers from the 'anchor_frames' column
        unique_frames = df['best_anchor_frame'].unique()

        # Define the video path
        video_name = os.path.splitext(os.path.basename(file))[0][:-9]
        current_video = f"{video_path}/{video_name}.MP4"

        # Step 2: Create a directory with the video name to store extracted frames
        output_folder = f"{files_path}/{video_name}"[:-9] + '_AnchorFrames'
        os.makedirs(output_folder, exist_ok=True)

        # Step 3: Use OpenCV to open the video and extract frames
        cap = cv2.VideoCapture(current_video)

        # Get the total number of frames in the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Check if the video opened successfully
        if not cap.isOpened():
            print("Error: Could not open the video.")
            continue
        else:
            print(f"Total frames in video: {total_frames}")

            # Step 4: Iterate through unique frames, read and save them
            for frame_no in unique_frames:
                # Ensure frame number is within the video frame range
                if frame_no >= 0 and frame_no < total_frames:
                    # Set the video frame to the specific frame number
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

                    # Read the frame
                    ret, frame = cap.read()

                    if ret:
                        # Create the filename for the frame
                        frame_filename = os.path.join(output_folder, f"{video_name}_frame{frame_no}.jpg")

                        # Save the frame as an image
                        cv2.imwrite(frame_filename, frame)
                    else:
                        print(f"Error: Could not read frame {frame_no}")
                else:
                    print(f"Frame number {frame_no} is out of bounds")

        # Release the video capture object
        cap.release()
        print('Frame extraction completed for video ' + video_name)
