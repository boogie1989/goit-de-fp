import os
import requests
from pyspark.sql import SparkSession
from config import LANDING_PATH, BRONZE_PATH

# --------------------------------------------
# Initialize Spark Session
# --------------------------------------------
spark = SparkSession.builder.appName("LandingToBronze").getOrCreate()

# --------------------------------------------
# FTP URLs and Destination Paths
# --------------------------------------------
FTP_URLS = {
    "athlete_bio": "https://ftp.goit.study/neoversity/athlete_bio.csv",
    "athlete_event_results": "https://ftp.goit.study/neoversity/athlete_event_results.csv"
}

# Ensure directories exist
os.makedirs(LANDING_PATH, exist_ok=True)
os.makedirs(BRONZE_PATH, exist_ok=True)

# --------------------------------------------
# Download Data Function
# --------------------------------------------
def download_data(table_name, url):
    local_file_path = os.path.join(LANDING_PATH, f"{table_name}.csv")
    print(f"Downloading from {url} to {local_file_path}")
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved as {local_file_path}")
    else:
        exit(f"Failed to download the file {table_name}. Status code: {response.status_code}")

# --------------------------------------------
# Download Files
# --------------------------------------------
for table, url in FTP_URLS.items():
    download_data(table, url)

# --------------------------------------------
# Convert CSV to Parquet
# --------------------------------------------
def csv_to_parquet(table_name):
    csv_file_path = os.path.join(LANDING_PATH, f"{table_name}.csv")
    parquet_file_path = os.path.join(BRONZE_PATH, table_name)
    
    # Read CSV file using Spark
    df = spark.read.csv(csv_file_path, header=True, inferSchema=True)
    print(f"Converting {csv_file_path} to {parquet_file_path}")
    
    # Save as Parquet
    df.write.mode("overwrite").parquet(parquet_file_path)
    print(f"Data saved to {parquet_file_path}")

# --------------------------------------------
# Process Each Table
# --------------------------------------------
for table in FTP_URLS.keys():
    csv_to_parquet(table)

print("Landing to Bronze process completed.")
