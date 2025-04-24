import pandas as pd 
import matplotlib as plot 
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import os
import argparse
from tqdm import tqdm

# Function that takes dataframe and number of anchor frame -> returns dataframe with 4 columns from 
# ( Territory ID - X - Y ) 

class territoryMatching:
    
    def __init__(self, file_metashape_anchor, file_dlc_anchor):
        """The class is used to load two files at a time, one having territories from meta shape and another having 
        territories from dlc. The class solves the problem of two territories having same ID. 

        Args:
            file_metashape_anchor (data frame): File with information of territories marked with meta shape
            file_dlc_anchor (_type_): File with information of territories marked with DLC + YOLO tracking 
        """
        # Constructor: initializes the class attributes
        self.metashpe_anchor = file_metashape_anchor
        self.dlc_anchor = file_dlc_anchor
        
        # Load data frames 
        self.t_id_anchor, self.t_id_dlc_anchor = self.loadData()
        
        # Get list of all anchor frames 
        self.anchor_frames = self.getAnchorFrames()
        # Get list of total number of frames in the video 
        self.total_no_of_frames = self.getFrameInformation()
        
        # Copy of the final file 
        self.t_id_dlc_updated = pd.DataFrame(columns=self.t_id_dlc_anchor.columns) # self.t_id_dlc_anchor.copy()
        self.t_id_dlc_updated["Point"] = None
        self.t_id_dlc_updated["Distance"] = None
        
    def getAnchorFrames(self):
        """Get information about total number of anchor frames 

        Returns:
            list : The id of all the anchor frames 
        """
        anchor_frames = self.t_id_anchor[self.t_id_anchor["Point"] == 1]["frame_seq"].tolist()
        return anchor_frames
    
    def getFrameInformation(self):
        """Get number of total frames 

        Returns:
            int: Total number of frames in the given video
        """
        max_frame_count = self.t_id_dlc_anchor["frame"].max()
        return max_frame_count
    
    def saveFinalMapping(self, file_name = "mapping.csv"):
        """Save the file with 
        """
        storage = file_name.split(".")[0]
        storage += "_matched.csv"
        self.t_id_dlc_updated.to_csv(storage, index = False)
    
    def startMatching(self,start_frame_count = 0, end_frame_count = 0, threshold = 50):
        """The function starts going through the DLC tracking file, for each frame it identifies all the territory mapping between territory ID given by DLC and territory ID given by meta shape.
        The resulting data frame is stored in the same folder with *csv name. 

        Args:
            start_frame_count (int, optional): The no of frame to process, ideally you want to process all. Defaults to 0.
            end_frame_count(int, optional) : The processing should stop at this frame number. 
            threshold (int, optional): Threshold for selection of territories for mapping, while finding nearest neighbor. Defaults to 50.
        """
        # Assuming all files start from frame 0, if not then we might have a problem 
        if end_frame_count == 0 or end_frame_count > self.total_no_of_frames:
            end_frame_count = self.total_no_of_frames  
        
        # Only process frames that actually exist in the DLC dataframe
        existing_frames = sorted(
            frame for frame in self.t_id_dlc_anchor['frame'].dropna().unique()
        )

        for query_frame in tqdm(existing_frames, desc="Frame processing"):

            t_id_anchor_filter, t_id_dlc_anchor_filter = self.extract_frame_info(query_frame)
            
            # Match the territory ID for the specific files 
            t_id_dlc_matching_information = self.match_information_dlc_to_meta(t_id_dlc_anchor_filter, t_id_anchor_filter, threshold )
            
            self.update_frame(t_id_dlc_matching_information)
            
    def extract_frame_info(self, query_frame):
        # Extract information for a particular query frame 
        t_id_dlc_anchor_filter = self.extract_frame_info_dlc(query_frame)
        t_id_anchor_filter = self.find_corresponding_frame_info_meta (t_id_dlc_anchor_filter)
        
        return t_id_anchor_filter, t_id_dlc_anchor_filter
            
    def find_corresponding_frame_info_meta(self,t_id_dlc_anchor_filter):
        # Extract information of the anchor frame relevant to the given query frame 
        matching_anchor_frame = t_id_dlc_anchor_filter["best_anchor_frame"].iloc[0]
        
        # Extract territory information for a particular anchor frame from meta shape file  
        return self.extract_frame_info_metashape(matching_anchor_frame)
            
    
    def loadData(self):
        df_id_anchor = pd.read_csv(self.metashpe_anchor)
        size = df_id_anchor.shape[0]
        df_id_anchor = df_id_anchor.dropna()
        
        df_id_dlc_anchor = pd.read_csv(self.dlc_anchor)
        size = df_id_dlc_anchor.shape[0]
        df_id_dlc_anchor = df_id_dlc_anchor.dropna()
        
        return df_id_anchor, df_id_dlc_anchor
    
    def update_frame(self, dlc_frame):
        # Compile the new file together 
        self.t_id_dlc_updated = pd.concat([self.t_id_dlc_updated, dlc_frame], ignore_index= True)

    def extract_frame_info_dlc(self, frameNo):
        # Extracting information about a specific frame 
        return self.t_id_dlc_anchor[self.t_id_dlc_anchor["frame"]== frameNo]
        

    def extract_frame_info_metashape(self, frameNo):
        # Extracting information about a specific frame 
        return self.t_id_anchor[self.t_id_anchor["frame_seq"] == frameNo]
        
            
    def plot_both_together(self, t_id_anchor_filter, t_id_dlc_anchor_filter):
        # Pass data frame for a particular frame 
        # Scatter plot for DataFrame 1
        plt.scatter(t_id_anchor_filter['u'], t_id_anchor_filter['v'], label='MetaShape', color='blue')
        for i, txt in enumerate(t_id_anchor_filter['Point']):
            plt.text(t_id_anchor_filter['u'].iloc[i], t_id_anchor_filter['v'].iloc[i], txt, fontsize=8, color='blue')

        # Scatter plot for DataFrame 2
        plt.scatter(t_id_dlc_anchor_filter['transformed_x'], t_id_dlc_anchor_filter['transformed_y'], label='DLC', color='red')
        for i, txt in enumerate(t_id_dlc_anchor_filter['idx']):
            plt.text(t_id_dlc_anchor_filter['transformed_x'].iloc[i]+90, t_id_dlc_anchor_filter['transformed_y'].iloc[i]+90, txt, fontsize=8, color='red')

        plt.xlabel('X Axis Label')
        plt.ylabel('Y Axis Label')
        plt.legend()
        plt.show()
        
    def plot_both_separately(self, t_id_anchor_filter, t_id_dlc_anchor_filter):

        # Create a figure with two subplots (1 row, 2 columns)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Scatter plot for DataFrame 1
        ax1.scatter(t_id_anchor_filter['u'], t_id_anchor_filter['v'], label='Dataset 1', color='blue')
        for i, txt in enumerate(t_id_anchor_filter['Point']):
            ax1.text(t_id_anchor_filter['u'].iloc[i], t_id_anchor_filter['v'].iloc[i], txt, fontsize=8, color='blue')

        ax1.set_title('Anchor metashape')
        ax1.set_xlabel('X Axis Label')
        ax1.set_ylabel('Y Axis Label')

        # Scatter plot for DataFrame 2
        ax2.scatter(t_id_dlc_anchor_filter['transformed_x'], t_id_dlc_anchor_filter['transformed_y'], label='Dataset 2', color='red')
        for i, txt in enumerate(t_id_dlc_anchor_filter['idx']):
            ax2.text(t_id_dlc_anchor_filter['transformed_x'].iloc[i]+90, t_id_dlc_anchor_filter['transformed_y'].iloc[i]+90, txt, fontsize=8, color='red')

        ax2.set_title('Anchor DLC')
        ax2.set_xlabel('X Axis Label')
        ax2.set_ylabel('Y Axis Label')

        plt.tight_layout()
        plt.show()
    
    
    def match_information_dlc_to_meta(self, t_id_dlc_anchor_filter, t_id_anchor_filter, threshold = 50): 
        """The function will find matching between the gien DLC dataframe slice with given meta shape territory file 

        Args:
            t_id_dlc_anchor_filter (_type_): Slice of DLC territory tracking file (YOLO)
            t_id_anchor_filter (_type_): Anchor file produced from metashape. 
            threshold (int, optional): Threshold for mapping consideration, territories above this distance will be deleted. Defaults to 50.

        Returns:
            data frame : data frame in same format as DLC territory tracking updated with IDs from meta shape anchor 
        """
        # Build KDTree from df2 coordinates
        tree = KDTree(t_id_anchor_filter[['u', 'v']])

        # Copy all content safely to another frame and prepare empty columns for updated information
        t_id_dlc = t_id_dlc_anchor_filter.copy()
        t_id_dlc.loc[:,"Point"] = 0
        t_id_dlc.loc[:,"Distance"] = 0
        
        # Find closest point in DLC for each point in df1
        for idx1, row1 in t_id_dlc_anchor_filter.iterrows():
                # Fine id for the closest point on tree 
                dist, idx2 = tree.query([row1['transformed_x'], row1['transformed_y']])
                # Look for the closest point in the anchor file 
                closest_point = t_id_anchor_filter.iloc[idx2]
                
                # Storing matched information 
                t_id_dlc.loc[idx1,"Point"] = closest_point["Point"]
                t_id_dlc.loc[idx1,"Distance"] = dist
                
        # Remove positions that have distance more than threshold values 
        t_id_dlc = t_id_dlc[t_id_dlc["Distance"] < threshold]
        # Remove all positions where matching is not found and Distance value is default
        t_id_dlc = t_id_dlc[t_id_dlc["Distance"] != 0]
        
        return t_id_dlc
        


def main(args):
    # Access command-line arguments via args.<argument_name>
    print(f"Input DLC folder: {args.dlc_folder}")
    print(f"Input Metashape file: {args.input_file_meta}")
    
    # Identify DLC files ending with "_Anchored.csv" and ignore hidden files
    dlc_files = [
        os.path.join(args.dlc_folder, file)
        for file in os.listdir(args.dlc_folder)
        if file.endswith('_Anchored.csv') and not file.startswith("._")  # Ignore hidden files
    ]

    if not dlc_files:
        raise FileNotFoundError(f"No valid files ending with '_Anchored.csv' found in the folder {args.dlc_folder}.")

    metashape_file = args.input_file_meta

    # Validate the DLC folder
    if not os.path.exists(args.dlc_folder) or not os.path.isdir(args.dlc_folder):
        raise FileNotFoundError(f"The folder {args.dlc_folder} does not exist or is not a directory.")

    # Validate the Metashape file
    if not os.path.exists(args.input_file_meta):
        raise FileNotFoundError(f"The file {args.input_file_meta} does not exist.")

    # Process each DLC file
    for dlc_file in dlc_files:
        matching = territoryMatching(file_dlc_anchor=dlc_file, file_metashape_anchor=args.input_file_meta)
        matching.startMatching()
        matching.saveFinalMapping(dlc_file)
    

if __name__ == "__main__":
    # Initialize parser
    parser = argparse.ArgumentParser(description="The script takes *csv files as input, finds territory mapping between DLC and metashape files.")

    # Add arguments
    parser.add_argument(
        "-d", "--dlc_folder", 
        type=str, 
        required=True, 
        help="Path to the directory containing the territory tracking '*_Anchored.csv' files",
    )
    
    parser.add_argument(
        "-m", "--input_file_meta", 
        type=str, 
        required=True, 
        help="Path to the Metashape CSV file",
    )
    
    # Parse arguments
    args = parser.parse_args()

    # Run main function
    main(args)
