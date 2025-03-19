import glob

from boxmot import OCSORT, BYTETracker
from bbtrack_yolo.BBoxDetection import BBoxDetection
from bbtrack_yolo.BBoxTracker import BBoxTracker

DATE = ['20230302', '20230303', '20230303', '20230303', '20230303', '20230305', '20230305', '20230306', '20230306', '20230306']
SESSION = ['SM_Lek1', 'SM_Lek1', 'SM_Lek1', 'SM_Lek1', 'SE_Lek1', 'SM_Lek1', 'SE_Lek1', 'SM_Lek1', 'SM_Lek1', 'SE_Lek1']
DRONE = ['P3D6', 'P3D6', 'P3D6', 'P3D6', 'P3D6', 'P3D6', 'P3D6', 'P1D2', 'P3D6', 'P3D6']
VIDEOS = ['0540', '0569', '0570', '0575', '0591', '0603', '0619', '0759', '0647', '0668']

file_directory = '/home/vsridhar/samba/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration'

for date,session,drone,video in zip(DATE,SESSION,DRONE,VIDEOS):
    internal_path = file_directory + '/' + date + '/' + session + '/' + drone
    file = internal_path + '/' + date + '_' + session + '_' + drone + '_DJI_' + video + '_YOLO.csv'
    
    # Load detections
    all_dets = BBoxDetection.load_from(file)

    # Initialize tracker
    tracker = BBoxTracker(tracker=OCSORT())

    # Track detections
    trks = tracker.track(all_dets)

    # Save tracks
    trks.save_to(file[:-4] + '_tracked.csv')
            
