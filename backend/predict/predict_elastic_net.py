import subprocess
import pandas as pd
import os
import time

def predict_elastic_net(df):
    # start time
    start = time.time()
    print("Predicting using elastic net models.")
    print("Using the example data file, this may take up to a minute.")

    # R script location
    r_script_path = "predict/predict.R"
    input_csv="predict/input.csv"
    output_csv="predict/predictions.csv"

    # save dv as a csv file
    # Ensure the input CSV file is in the correct format
    df.to_csv(input_csv, index=True) 
    print("calling R script...")
    print()
    try:
        # Run the R script
        subprocess.run(
            ["Rscript", r_script_path],
            check=True,
            capture_output=True,
            text=True
        )
        # Load the predictions into a Pandas DataFrame
        predictions = pd.read_csv(output_csv, index_col=0)
        return predictions
    except subprocess.CalledProcessError as e:
        print("Error during R script execution:")
        print(e.stderr)
        return pd.DataFrame()
    finally:
        # Clean up temporary files
        if os.path.exists(input_csv):
            os.remove(input_csv)
        if os.path.exists(output_csv):
            os.remove(output_csv)
        # end time
        end = time.time()
        print(f"Time for model loading, EN predictions, minor R data formatting: {end - start} seconds")

