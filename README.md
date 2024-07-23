`01PX_TerritoryDetection_Training.ipynb` contains code to train the territory detection model using DLC.
Here, X can be 1,2 or 3 and refers to the corresponding position on the lek i.e., P1, P2 or P3.

`02PX_TerritoryDetection_Inference.ipynb` contains code to run inference using the territory detection model trained above.

`03_TerritoryDetection_Visualise.ipynb` contains code to visualise results of the inference code.

Note that territory detection using DLC does not do tracking, i.e., it does not propagate territory IDs across frames. To try and do this, I implemented the Hungarian algorithm to propagate territory IDs through frames. This is presented in `04_TerritoryTracking_Hungarian.ipynb`. However, this does not seem to do the best job and tracking territories seems to require a different algorithm / combination of algorithms.
