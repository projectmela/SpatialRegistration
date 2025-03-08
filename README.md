This repository focuses on georeferencing the movement data obtained from tracking our blackbuck videos. The output of these series of scripts will be lat-lon coordinates of all the tracked animals, thus placing data from several drones within the same coordinate reference. Note that this entire pipeline needs to follow the creation of an orthomosaic where we will embed the movement data.


### Step 1: Track stationary markers in the environment (in this case, the blackbuck territories)

The first step of the registration process is to have a track the blackbuck territory markings. Since these are stationary features in the environment—features with known coordinates in our orthomosaic—we can use this tracking output in subsequent steps to map image coordinates to world coordinates.

`01PX_TerritoryDetection_Training.ipynb` contains code to train the territory detection model using DLC.
Here, X can be 1,2 or 3 and refers to the corresponding position on the lek i.e., P1, P2 or P3.

`02PX_TerritoryDetection_Inference.ipynb` contains code to run inference using the territory detection model trained above.

`03_TerritoryDetection_Visualise.ipynb` contains code to visualise results of the inference code. This of course need not be run on all the videos but it is a good way to get a visual impression of the detection quality.

Note that territory detection using DLC does not do tracking, i.e., it does not propagate territory IDs across frames. The following two steps are meant to deal with this problem. `04_TerritoryDetection_ConvertYOLO.ipynb` converts the detections from the DLC format to a YOLO format. `05_TerritoryTracking_BYTE.py` then uses the BYTE tracker to track these territories.

This completes step 1 of the registration process.


### Step 2: Register the stationary markers to the orthomosaic (used to compute error in our pipeline)

The second step of the registration process is actually registering video frames to the orthomosaic using Agisoft Metashape. One caveat here is that we cannot register all frames from our videos to the orthomosaic. This is time-intensive, computationally expensive, and impractical. We will therefore identify select frames, called anchor frames, that we will register to the orthomosaic with Metashape. We will then use homography (on the tracked territory points from step 1) to get transformation matrices to go from the rest of our frames to their corresponding anchor frames. Note that a key thing to sort out for step 2 tis to match territory identities from the tracked videos in step 1 and the identities in the orthomosaic. These identity correspondences are important for homography to work.

`06_TransformToAnchorCoordinates.ipynb` identifies potential anchor frames based on movement of the drone and assigns the best anchor frame for each frame in the video. It also transforms territory coordinates in each frame to the coordinates they would occupy once transformed to their best anchor frame.

`07_IsolateAnchorFrames.ipynb` goes through the videos and creates a folder where it isolates all anchor frames. The frames are then registered to the orthomosaic within Metashape. This registration is essentially a process of computing the pose of the camera when that frame whas captured such that the image is registered as well as possible with the orthomosaic. I consider this registrations to be a step of its own i.e., `08_RegisterAnchorFrames`. Since this is not done using code, we do not have a script. But to acknowledge the step, I have still prefixed the next step with a `09`.

`09_ProjectTerritoriesToAnchors.py` takes all labelled territories in the orthomosaic and projects onto the anchor frames. 
Run this script within Agisoft Metashape's Python API.

`10_TerritoryIDMatch.py` takes the territory IDs projected onto anchor frames in step `09_ProjectTerritoriesToAnchors.py` and uses these to correct IDs of territories from our tracking. 
Run this script using the following command in the terminal `python3 10_TerritoryIDMatch.py -d "path/to/directory/with/*_Anchored.csv/files" -m "path/to/projected/territories/on/anchors"`.

`11_ReformatMatchedTerritories.ipynb` is a simple reformatting step. We do this to make our next step easier.

`12_UnprojectTrackedTerritories.py` unprojects all territory coordinates from our initial tracking onto the orthomosaic. At the end of this step, we have successfully transformed our territory locations from image coordinates to geospatial coordinates!!!
Run this script within Agisoft Metashape's Python API.

We can easily use this output and compare our unprojected territory coordinates with the ground truth (marked on our orthomosaic) to calculate the average error in our pipeline.


### Step 3: Register the moving objects of interest to the orthomosaic

The final step of this pipeline involves transforming coordinates from our blackbuck tracking to geospatial coordinates. The steps are analogous to coordinate transformation done for the territories in step 2. So each script in step 3 will ideally have its parallel in step 2.

`13_TransformTrajectoriesToAnchors.ipynb` transforms movement coordinates of the blackbuck from their current frame to their best anchor frame. The best anchor frame is the same as calculated in `06_TransformToAnchorCoordinates.ipynb`. `13_TransformTrajectoriesToAnchors.ipynb` has `06_TransformToAnchorCoordinates.ipynb` as its analogous script in step 2.

`14_ReformatAnchoredTrajectories.ipynb` is a simple reformatting step. We do this to make our next step easier. `14_ReformatAnchoredTrajectories.ipynb` has `11_ReformatMatchedTerritories.ipynb` as its analogous script in step 2.

`15_UnprojectTrajectories.py` unprojects all trajectory coordinates from our initial tracking onto the orthomosaic. At the end of this step, we have successfully georeferenced all our blackbuck movement data!!! `15_UnprojectTrajectories.py` has `12_UnprojectTrackedTerritories.py` as its analogous script in step 2.
Run this script within Agisoft Metashape's Python API.

Thus ends our spatial registration odyssey!

