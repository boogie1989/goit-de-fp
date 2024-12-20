import os
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
from config import BRONZE_PATH, SILVER_PATH

# --------------------------------------------
# Initialize Spark Session
# --------------------------------------------
spark = SparkSession.builder.appName("BronzeToSilver").getOrCreate()

# Ensure directories exist
os.makedirs(SILVER_PATH, exist_ok=True)

# --------------------------------------------
# Function to Clean Text Data
# --------------------------------------------
def clean_text(text):
    """Remove special characters from text."""
    return re.sub(r'[^a-zA-Z0-9,.\\"\']', '', str(text))

# Create a Spark UDF (User Defined Function) for text cleaning
clean_text_udf = udf(clean_text, StringType())

# --------------------------------------------
# Process Bronze Table
# --------------------------------------------
def process_bronze_table(table_name):
    bronze_table_path = os.path.join(BRONZE_PATH, table_name)
    silver_table_path = os.path.join(SILVER_PATH, table_name)

    # Read the bronze table in Parquet format
    print(f"Reading data from {bronze_table_path}")
    df = spark.read.parquet(bronze_table_path)

    # Clean all string columns in the DataFrame
    for col_name, col_type in df.dtypes:
        if col_type == 'string':
            df = df.withColumn(col_name, clean_text_udf(col(col_name)))

    # Deduplicate rows
    df_dedup = df.dropDuplicates()

    # Write the cleaned and deduplicated data to the silver layer
    print(f"Writing cleaned data to {silver_table_path}")
    df_dedup.write.mode("overwrite").parquet(silver_table_path)

# --------------------------------------------
# List of Tables to Process
# --------------------------------------------
tables = ["athlete_bio", "athlete_event_results"]

# Process Each Table
for table in tables:
    process_bronze_table(table)

print("Bronze to Silver process completed.")
