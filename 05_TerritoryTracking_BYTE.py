import glob

from boxmot import OCSORT, BYTETracker
from bbtrack_yolo.BBoxDetection import BBoxDetection
from bbtrack_yolo.BBoxTracker import BBoxTracker

DATE = ['20230318']#, '20230317', '20230318']
SESSION = ['SM_Lek1']#, 'SE_Lek1']
DRONE = ['P3D5']#, 'P1D2', 'P2D3', 'P2D4', 'P3D5', 'P3D6']

file_directory = '/home/vsridhar/samba/blackbuck/working/processed/TerritoryDetection2023/SSD7'

for date in DATE:
    for session in SESSION:
        for drone in DRONE:
            internal_path = file_directory + '/' + date + '/' + session + '/' + drone
            files = glob.glob(internal_path + '/' + date + '_' + session + '_' + drone + '_*YOLO.csv')
            
            for file in files:
            	# Load detections
            	all_dets = BBoxDetection.load_from(file)
            	
            	# Initialize tracker
            	tracker = BBoxTracker(tracker=BYTETracker())
            	
            	# Track detections
            	trks = tracker.track(all_dets)
            	
            	# Save tracks
            	trks.save_to(file[:-4] + '_tracked.csv')
		
