This repository focuses on georeferencing the movement data obtained from tracking our blackbuck videos. The output of these series of scripts will be lat-lon / UTM coordinates of all the tracked animals, thus placing data from several drones within the same coordinate reference. Note that this entire pipeline needs to follow the creation of an orthomosaic with hand annotations of stationary markers on it. The pipeline will embed our movement data on this orthomosaic while using coordinates of the stationary markers to compute errors.

Note: While the description below focuses on the steps to run the overall pipeline, the repository also contains some helper functions that allow for cleaner code and effective scripting of these steps. These helper functions are essential to run scripts within the pipeline so ensure that they're imported appropriately by their parent scripts.

### Step 1: Track stationary markers in the environment (in this case, the blackbuck territories)

The first step of the registration process is to track the blackbuck territory markings. Since these are stationary features in the environment, features with known coordinates in our orthomosaic, we can use this tracking output in subsequent steps to map image coordinates to world coordinates and subsequently compute errors by comparing the computed territory coordinates with previous annotations of these coordinates.

`01_TerritoryDetection_Training.ipynb` contains code to train the territory detection model using DLC.

`02_TerritoryDetection_Inference.ipynb` contains code to run inference using the territory detection model trained above.

`03_TerritoryDetection_Visualise.ipynb` contains code to visualise results of the inference code. This of course need not be run on all the videos but it is a good way to get a visual impression of the detection quality.

Note that territory detection using DLC does not do tracking, i.e., it does not propagate territory IDs across frames. The following two steps are meant to deal with this problem. `04_TerritoryDetection_ConvertYOLO.ipynb` converts the detections from the DLC format to a YOLO format. `05_TerritoryTracking_BYTE.py` then uses the BYTE tracker to track these territories. One could equally easily track these territories using YOLO11 and BYTETracker (state-of-the-art at the time of writing this documentation) to reduce the number of steps indicated in this pipeline.

This completes step 1 of the registration process.


### Step 2: Register the stationary markers to the orthomosaic (used to compute error in our pipeline)

The second step of the registration process is actually registering video frames to the orthomosaic using Agisoft Metashape. One caveat here is that we cannot register all frames from our videos to the orthomosaic. This is time-intensive, computationally expensive, and impractical. We therefore identify select frames, called anchor frames, that we register to the orthomosaic with Metashape. We then use homography (on the tracked territory points from step 1) to get transformation matrices to go from the rest of our frames to their corresponding anchor frames. Note that in order to compute the error in our overall registration, we will need ID correspondences between territories tracked from videos in step 1 and territory identities in the orthomosaic.

`06_TransformToAnchorCoordinates.ipynb` identifies potential anchor frames based on movement of the drone (rotation, translation and scaling of image features) and assigns the best anchor frame for each frame in the video. It also transforms territory coordinates in each frame to the coordinates they would occupy once transformed to their best anchor frame.

`07_IsolateAnchorFrames.ipynb` goes through the videos and creates a folder where it isolates all anchor frames. The frames are then registered to the orthomosaic within Metashape. This registration is essentially a process of computing the pose of the camera when that frame whas captured such that the image is registered as well as possible with the orthomosaic. I consider this registrations to be a step of its own i.e., `08_RegisterAnchorFrames`. Since this is not done using code, we do not have a script. But to acknowledge the step, I have still prefixed the next step with a `09`.

`09_ProjectTerritoriesToAnchors.py` takes all labelled territories in the orthomosaic and projects onto the anchor frames. 
Run this script within Agisoft Metashape's Python API.

`10_TerritoryIDMatch.py` takes the territory IDs projected onto anchor frames in step `09_ProjectTerritoriesToAnchors.py` and uses these to correct IDs of territories from our tracking. 
Run this script using the following command in the terminal `python3 10_TerritoryIDMatch.py -d "path/to/directory/with/*_Anchored.csv/files" -m "path/to/projected/territories/on/anchors"`.

`11_ReformatMatchedTerritories.ipynb` is a simple reformatting step. We do this to make our next step easier.

`12_UnprojectTrackedTerritories.py` unprojects all territory coordinates from our initial tracking onto the orthomosaic. At the end of this step, we have successfully transformed our territory locations from image coordinates to geospatial coordinates!!!
Run this script within Agisoft Metashape's Python API.

Finally, we run `13_ComputeError_PlotTrajectories.ipynb` to compare the above output (coordinates of the unprojected territories) with the ground truth (coordinates marked on our orthomosaic) to calculate the average error in our pipeline. Technically, we now have everything we need for the registration pipeline—the transformation matrices and an error measure to validate the pipeline. We only have to apply the right transformations to the blackbuck trajectories now and voila, we'll have blackbuck movement in geospatial coordinates!

### Step 3: Register the moving objects of interest to the orthomosaic

As described above, the final step of this pipeline involves transforming coordinates from our blackbuck tracking to geospatial coordinates. The steps are analogous to coordinate transformation done for the territories in step 2. So each script in step 3 will ideally have its parallel in step 2.

`14_TransformTrajectoriesToAnchors.ipynb` transforms movement coordinates of the blackbuck from their current frame to their best anchor frame. The best anchor frame is the same as calculated in `06_TransformToAnchorCoordinates.ipynb`. `14_TransformTrajectoriesToAnchors.ipynb` has `06_TransformToAnchorCoordinates.ipynb` as its analogous script in step 2.

`15_ReformatAnchoredTrajectories.ipynb` is a simple reformatting step. We do this to make our next step easier. `15_ReformatAnchoredTrajectories.ipynb` has `11_ReformatMatchedTerritories.ipynb` as its analogous script in step 2.

`16_UnprojectTrajectories.py` unprojects all trajectory coordinates from our initial tracking onto the orthomosaic. At the end of this step, we have successfully georeferenced all our blackbuck movement data!!! `16_UnprojectTrajectories.py` has `12_UnprojectTrackedTerritories.py` as its analogous script in step 2.
Run this script within Agisoft Metashape's Python API.

Thus ends our spatial registration odyssey! Thank you for joining me on this journey.

