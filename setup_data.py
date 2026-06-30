import os
import kagglehub

def setup():
    # Target directory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    # Ensure data folder exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Check if data directory already has files (excluding hidden/placeholder files)
    files = [f for f in os.listdir(data_dir) if not f.startswith(".")]
    
    if len(files) == 0:
        print("Data directory is empty. Fetching dataset 'nitishabharathi/indian-government-schemes'...")
        try:
            download_path = kagglehub.dataset_download(
                "nitishabharathi/indian-government-schemes",
                output_dir=data_dir
            )
            print(f"Dataset successfully downloaded to: {download_path}")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            print("Please make sure 'kagglehub' is installed and your Kaggle API credentials are set if required.")
    else:
        print(f"Data directory already contains files: {files}. Skipping download.")

if __name__ == "__main__":
    setup()
