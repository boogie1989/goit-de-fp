SUFFIX = "SerhiiB"

db_config = {
    "url": "jdbc:mysql://217.61.57.46:3306/olympic_dataset",
    "username": "neo_data_admin",
    "password": "Proyahaxuqithab9oplp",
    "db": "athlete_bio",
    "driver": "com.mysql.cj.jdbc.Driver",
    "output_db_url": "jdbc:mysql://localhost:3306/SerhiiB",
    "output_db": "athlete_enriched_results"
}

kafka_config = {
    "bootstrap_servers": ['localhost:29092'],
}

ATHLETE_TOPIC_NAME = f"athletes_{SUFFIX}"
OUTPUT_TOPIC_NAME = f"output_{SUFFIX}"
GOLD = "Gold"
SILVER = "Silver"
BRONZE = "Bronze"