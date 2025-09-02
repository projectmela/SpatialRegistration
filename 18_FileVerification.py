import os
from collections import defaultdict

# Paths (adjust if needed)
rawdata_root = '/Volumes/EAS_shared/blackbuck/working/rawdata/Field_Recording_2023/Original/lekking/20230316/SE_Lek1/'
processed_root = '/Volumes/EAS_shared/blackbuck/working/processed/Field_Recording_2023/SpatialRegistration/20230316/SE_Lek1/'

# Define global required suffixes (apply to all sessions)
global_required_suffixes = [
    '_3D_trajectories_utm.csv',
    '_3D_trajectories.csv',
    '_Anchored_trajectories.csv',
    '_3D_territories_utm.csv',
    '_3D_territories.csv',
    '_Anchored_matched.csv',
    '_Metashape_uv.csv',
    '_trajectories_uv.csv',
    '_homographies.pkl',
    '_Anchored.csv',
    '_YOLO_tracked.csv',
    '_YOLO.csv'
]

# Define position-specific DLC suffixes
position_dlc_suffixes = {
    "P1": [
        'DLC_dlcrnetms5_06_TerritoryDetectionP1Aug1shuffle1_50000_assemblies.pickle',
        'DLC_dlcrnetms5_06_TerritoryDetectionP1Aug1shuffle1_50000_el.h5',
        'DLC_dlcrnetms5_06_TerritoryDetectionP1Aug1shuffle1_50000_el.pickle',
        'DLC_dlcrnetms5_06_TerritoryDetectionP1Aug1shuffle1_50000_full.pickle',
        'DLC_dlcrnetms5_06_TerritoryDetectionP1Aug1shuffle1_50000_meta.pickle'
    ],
    "P2": [
        'DLC_dlcrnetms5_05_TerritoryDetectionP2Jul10shuffle1_50000_assemblies.pickle',
        'DLC_dlcrnetms5_05_TerritoryDetectionP2Jul10shuffle1_50000_el.h5',
        'DLC_dlcrnetms5_05_TerritoryDetectionP2Jul10shuffle1_50000_el.pickle',
        'DLC_dlcrnetms5_05_TerritoryDetectionP2Jul10shuffle1_50000_full.pickle',
        'DLC_dlcrnetms5_05_TerritoryDetectionP2Jul10shuffle1_50000_meta.pickle'
    ],
    "P3": [
        'DLC_dlcrnetms5_07_TerritoryDetectionP3Aug18shuffle1_50000_assemblies.pickle',
        'DLC_dlcrnetms5_07_TerritoryDetectionP3Aug18shuffle1_50000_el.h5',
        'DLC_dlcrnetms5_07_TerritoryDetectionP3Aug18shuffle1_50000_el.pickle',
        'DLC_dlcrnetms5_07_TerritoryDetectionP3Aug18shuffle1_50000_full.pickle',
        'DLC_dlcrnetms5_07_TerritoryDetectionP3Aug18shuffle1_50000_meta.pickle'
    ]
}

# Collect raw video IDs
raw_videos = defaultdict(list)
for subdir, _, files in os.walk(rawdata_root):
    for f in files:
        if f.endswith(('.MP4', '.mp4')):
            base, _ = os.path.splitext(f)
            parts = base.split("_")
            if len(parts) >= 5:
                video_id = "_".join(parts[:5])  # up to DJI_xxxx
                raw_videos[video_id].append(f)

# Collect processed files grouped by video id + session
processed_files = defaultdict(lambda: defaultdict(list))
for session in ['P1D1', 'P1D2', 'P2D3', 'P2D4', 'P3D5', 'P3D6']:
    folder_path = os.path.join(processed_root, session)
    if not os.path.isdir(folder_path):
        continue
    for f in os.listdir(folder_path):
        full_path = os.path.join(folder_path, f)
        if os.path.isfile(full_path):
            base, ext = os.path.splitext(f)
            for vid in raw_videos.keys():
                if base.startswith(vid):
                    suffix = base[len(vid):] + ext
                    processed_files[session][vid].append(suffix.lstrip("_"))
                    break

# Compare and report
for session, videos in processed_files.items():
    position = session[:2]  # "P1", "P2", "P3"
    for video_id, found_suffixes in videos.items():
        # Start with global suffixes
        required_suffixes = global_required_suffixes[:]
        # Add DLC suffixes for this position
        if position in position_dlc_suffixes:
            required_suffixes += position_dlc_suffixes[position]
        
        # Add the DJI-numbered CSVs as required
        # These are any found numeric CSVs in the processed folder
        numeric_csvs = [fs for fs in found_suffixes if fs.endswith(".csv") and fs.rstrip(".csv").isdigit()]
        required_suffixes += numeric_csvs

        # Check required files
        missing = [req for req in required_suffixes if req not in found_suffixes]
        if missing:
            print(f"\n⚠️ {video_id} (session {session}, {position}) is missing:")
            for s in missing:
                print(f"   - {s}")

        # Check unexpected files
        unexpected = [fs for fs in found_suffixes if fs not in required_suffixes]
        if unexpected:
            print(f"\n⚠️ {video_id} (session {session}, {position}) has unexpected files:")
            for s in unexpected:
                print(f"   - {s}")
