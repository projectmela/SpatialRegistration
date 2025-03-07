This repository focuses on georeferencing the movement data obtained from tracking our blackbuck videos. The output of these series of scripts will be lat-lon coordinates of all the tracked animals, thus placing data from several drones within the same coordinate reference.


### Step 1

The first step of the registration process is to have a track the blackbuck territory markings. Since these are stationary features in the environment—features with known coordinates in our orthomosaic—we can use this tracking output in subsequent steps to map image coordinates to world coordinates.

`01PX_TerritoryDetection_Training.ipynb` contains code to train the territory detection model using DLC.
Here, X can be 1,2 or 3 and refers to the corresponding position on the lek i.e., P1, P2 or P3.

`02PX_TerritoryDetection_Inference.ipynb` contains code to run inference using the territory detection model trained above.

`03_TerritoryDetection_Visualise.ipynb` contains code to visualise results of the inference code. This of course need not be run on all the videos but it is a good way to get a visual impression of the detection quality.

Note that territory detection using DLC does not do tracking, i.e., it does not propagate territory IDs across frames. The following two steps are meant to deal with this problem. `04_TerritoryDetection_ConvertYOLO.ipynb` converts the detections from the DLC format to a YOLO format. `05_TerritoryTracking_BYTE.py` then uses the BYTE tracker to track these territories.

This completes step 1 of the registration process.


### Step 2

The second step of the registration process is actually registering video frames to the orthomosaic using Agisoft Metashape. One caveat here is that we cannot register all frames from our videos to the orthomosaic. This is time-intensive, computationally expensive, and impractical. We will therefore identify select frames, called anchor frames, that we will register to the orthomosaic with Metashape. We will then use homography (on the tracked territory points from step 1) to get transformation matrices to go from the rest of our frames to their corresponding anchor frames. Note that a key thing to sort out for step 2 tis to match territory identities from the tracked videos in step 1 and the identities in the orthomosaic. These identity correspondences are important for homography to work.

`06_TransformToAnchorCoordinates.ipynb` identifies potential anchor frames based on movement of the drone and assigns the best anchor frame for each frame in the video.

`07_IsolateAnchorFrames.ipynb` goes through the videos and creates a folder where it isolates all anchor frames. The frames are then registered to the orthomosaic within Metashape. I consider this registrations to be a step of its own i.e., `08_RegisterAnchorFrames`. Since this is not done using code, we do not have a script. But to acknowledge the step, I have still prefixed the next step with a `09`.

`09_ProjectTerritoriesToAnchors.py`

`10_TerritoryIDMatch.py`

Run this script using the following command in the terminal `python3 10_TerritoryIDMatch.py -d "path/to/directory/with/*_Anchored.csv/files" -m "path/to/projected/territories/on/anchors"`.


### Step 3
