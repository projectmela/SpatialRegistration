import numpy as np
import pandas as pd

import cv2
import math
import time


# Helper functions

# Function to compute homography and extract translation, rotation, and scale
def compute_translation_rotation_scale(H):
    # Extract translation in x and y
    t_x = H[0, 2]
    t_y = H[1, 2]
    translation_xy = np.sqrt(t_x**2 + t_y**2)
    
    # Extract rotation angle from the top-left 2x2 submatrix
    r_11, r_21 = H[0, 0], H[1, 0]
    rotation_angle = math.atan2(r_21, r_11) * (180 / np.pi)  # convert to degrees
    
    # Extract scale factor from H[2, 2]
    scale_factor = 1 / H[2, 2]  # Inverse of the bottom-right value
    
    return translation_xy, rotation_angle, scale_factor


def identify_anchor_frames(df, thresholds):
    start_time = time.time()
    
    # Initialize variables
    anchor_frames = [0]  # Start with frame 0 as the first anchor frame
    
    # Get unique frames, sorted to process in order
    unique_frames = sorted(df['frame'].unique())
    
    # Set initial anchor frame
    anchor_frame = 0
    
    for frame in unique_frames:
        if frame == anchor_frame:
            continue
        
        # Get points in the current frame and anchor frame
        current_points = df[df['frame'] == frame][['idx', 'x', 'y']]
        anchor_points = df[df['frame'] == anchor_frame][['idx', 'x', 'y']]
        
        # Merge points on 'idx' to get corresponding points
        merged_points = pd.merge(current_points, anchor_points, on='idx', suffixes=('_current', '_anchor'))
        
        if len(merged_points) < 4:
            print(f"Not enough matching points for homography between frame {anchor_frame} and frame {frame}.")
            continue
        
        src_pts = merged_points[['x_anchor', 'y_anchor']].values
        dst_pts = merged_points[['x_current', 'y_current']].values
        
        # Apply RANSAC to find homography
        try:
            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
        except cv2.error as e:
            print(f"Homography calculation failed between frame {anchor_frame} and frame {frame}: {e}")
            continue
        
        # Calculate translation, rotation, and scale
        translation_xy, rotation_angle, scale_factor = compute_translation_rotation_scale(H)
        
        # Determine if the thresholds are exceeded
        threshold_exceeded = (translation_xy > thresholds['T_translation']) or \
                             (abs(rotation_angle) > thresholds['T_rotation']) or \
                             (abs(scale_factor - 1) > thresholds['T_scale'])
                             
        if threshold_exceeded:
            anchor_frames.append(frame)
            anchor_frame = frame  # Update the anchor frame
    
    end_time = time.time()
    print('Initial identification of anchors takes ', end_time - start_time)
    
    return anchor_frames


def find_best_anchor_for_each_frame(df, anchor_frames, thresholds):
    start_time = time.time()
    
    # Create a new column to store the best anchor frame for each frame
    df['best_anchor_frame'] = np.nan
    
    # Loop through all frames
    unique_frames = sorted(df['frame'].unique())
    
    for frame in unique_frames:
        # If the frame itself is an anchor, set itself as the anchor
        if frame in anchor_frames:
            df.loc[df['frame'] == frame, 'best_anchor_frame'] = frame
            continue
        
        # Compare against all preceding anchor frames
        best_anchor = None
        best_inliers = 0  # To keep track of the best match based on inliers
        
        for anchor_frame in anchor_frames:
            # Get points in the current frame and the candidate anchor frame
            current_points = df[df['frame'] == frame][['idx', 'x', 'y']]
            anchor_points = df[df['frame'] == anchor_frame][['idx', 'x', 'y']]
            
            # Merge points on 'idx' to get corresponding points
            merged_points = pd.merge(current_points, anchor_points, on='idx', suffixes=('_current', '_anchor'))
            
            if len(merged_points) < 4:
                continue  # Skip if not enough points to calculate homography
            
            src_pts = merged_points[['x_anchor', 'y_anchor']].values
            dst_pts = merged_points[['x_current', 'y_current']].values
            
            # Apply RANSAC to find homography
            try:
                H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
                inliers_count = np.sum(mask)  # Number of inliers
            except cv2.error as e:
                continue  # Skip if homography calculation failed
            
            # If this anchor frame gives more inliers, choose it as the best anchor
            if inliers_count > best_inliers:
                best_anchor = anchor_frame
                best_inliers = inliers_count
        
        # Assign the best anchor for the current frame
        if best_anchor is not None:
            df.loc[df['frame'] == frame, 'best_anchor_frame'] = best_anchor
    
    end_time = time.time()
    print('Finding the best anchors takes ', end_time - start_time)
    
    return df


def apply_homography_to_best_anchor(df):
    start_time = time.time()
    
    homography_matrices = {}  # Dictionary to store homography matrices
    rms_errors = {}  # Dictionary to store RMS errors for each frame
    
    # Initialize with the identity matrix for frame 0
    identity_matrix = np.eye(3)
    homography_matrices[0] = identity_matrix  # Frame 0 is its own anchor
    rms_errors[0] = 0  # No error for frame 0 as it's its own anchor
    
    df['transformed_x'] = np.nan
    df['transformed_y'] = np.nan
    
    unique_frames = sorted(df['frame'].unique())
    
    for frame in unique_frames:
        best_anchor_frame = df.loc[df['frame'] == frame, 'best_anchor_frame'].values[0]
        
        if frame == best_anchor_frame:
            # If the frame is its own anchor, copy the coordinates directly
            df.loc[df['frame'] == frame, 'transformed_x'] = df['x']
            df.loc[df['frame'] == frame, 'transformed_y'] = df['y']
            
            # Store identity matrix for this frame in the dictionary
            homography_matrices[frame] = identity_matrix
            continue
        
        # Get points in the current frame and its best anchor frame
        current_points = df[df['frame'] == frame][['idx', 'x', 'y']]
        anchor_points = df[df['frame'] == best_anchor_frame][['idx', 'x', 'y']]
        
        # Merge points on 'idx' to get corresponding points
        merged_points = pd.merge(current_points, anchor_points, on='idx', suffixes=('_current', '_anchor'))
        
        if len(merged_points) < 4:
            print(f"Not enough matching points for homography between frame {best_anchor_frame} and frame {frame}.")
            continue
        
        src_pts = merged_points[['x_anchor', 'y_anchor']].values
        dst_pts = merged_points[['x_current', 'y_current']].values
        
        # Apply RANSAC to find homography
        try:
            H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
            homography_matrices[frame] = H  # Store the homography matrix for this frame
        except cv2.error as e:
            print(f"Homography calculation failed between frame {best_anchor_frame} and frame {frame}: {e}")
            continue
        
        # Transform only the matched points using the homography matrix
        transformed_pts = cv2.perspectiveTransform(np.array([dst_pts], dtype=np.float32), H)[0]
        
        # Update DataFrame with transformed coordinates
        for idx, (x, y) in zip(merged_points['idx'], transformed_pts):
            df.loc[(df['frame'] == frame) & (df['idx'] == idx), 'transformed_x'] = x
            df.loc[(df['frame'] == frame) & (df['idx'] == idx), 'transformed_y'] = y
        
        # Calculate the RMS error (Euclidean distance between transformed and anchor points)
        errors = np.linalg.norm(transformed_pts - src_pts, axis=1)
        rms_error = np.sqrt(np.mean(errors**2))
        rms_errors[frame] = rms_error
    
    end_time = time.time()
    print('Applying homography to the best anchors takes ', end_time - start_time)
    
    return df, homography_matrices, rms_errors