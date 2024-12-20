import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, current_timestamp, date_format
from config import SILVER_PATH, GOLD_PATH
from spark import create_spark_session

# Ensure directories exist
os.makedirs(GOLD_PATH, exist_ok=True)

spark = create_spark_session('SilverToGold')

# --------------------------------------------
# Read Silver Tables
# --------------------------------------------
# Read athlete_bio table from silver layer
silver_athlete_bio_path = os.path.join(SILVER_PATH, "athlete_bio")
print(f"Reading data from {silver_athlete_bio_path}")
df_athlete_bio = spark.read.parquet(silver_athlete_bio_path)

# Read athlete_event_results table from silver layer
silver_event_results_path = os.path.join(SILVER_PATH, "athlete_event_results")
print(f"Reading data from {silver_event_results_path}")
df_event_results = spark.read.parquet(silver_event_results_path)

# --------------------------------------------
# Rename country_noc in one of the DataFrames to avoid ambiguity
# --------------------------------------------
df_event_results = df_event_results.withColumnRenamed("country_noc", "event_country_noc")

# --------------------------------------------
# Join Tables on athlete_id
# --------------------------------------------
df_joined = df_event_results.join(
    df_athlete_bio,
    on="athlete_id",
    how="inner"
)

# --------------------------------------------
# Calculate Average Height and Weight
# --------------------------------------------
avg_df = df_joined.groupBy(
    "sport", "medal", "sex", "event_country_noc"
).agg(
    avg("height").alias("avg_height"),
    avg("weight").alias("avg_weight"),
    current_timestamp().alias("timestamp")
).withColumn(
    "timestamp", date_format("timestamp", "yyyy-MM-dd HH:mm:ss")
)

# --------------------------------------------
# Show the Final DataFrame
# --------------------------------------------
print("Final Aggregated DataFrame:")
avg_df.show(truncate=False)

# --------------------------------------------
# Write Data to Gold Layer
# --------------------------------------------
gold_output_path = os.path.join(GOLD_PATH, "avg_stats")

print(f"Writing aggregated data to {gold_output_path}")
avg_df.write.mode("overwrite").parquet(gold_output_path)

print("Silver to Gold process completed.")

