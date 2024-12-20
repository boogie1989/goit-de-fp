
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, current_timestamp, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import json
from kafka import KafkaProducer
from threading import Thread
from config import db_config, kafka_config, ATHLETE_TOPIC_NAME, OUTPUT_TOPIC_NAME

os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 pyspark-shell'

KAFKA_SERVERS = kafka_config["bootstrap_servers"][0]

# Створення Spark сесії
spark = SparkSession.builder \
    .appName("EndToEndStreamingPipeline") \
    .config("spark.jars", "jars/mysql-connector-j-8.0.32.jar") \
    .getOrCreate()

# Функція для зчитування даних із MySQL
def read_athlete_bio():
    return spark.read.format('jdbc').options(
        url=db_config["url"],
        driver=db_config["driver"],
        dbtable=db_config["db"],
        user=db_config["username"],
        password=db_config["password"]
    ).load()

# Функція для фільтрації некоректних даних
def filter_invalid_data(df):
    return df.filter(
        (col("height").isNotNull()) & (col("weight").isNotNull()) &
        (col("height").cast("double").isNotNull()) & (col("weight").cast("double").isNotNull())
    )

# Функція для відправлення даних у Kafka
def send_to_kafka():
    # Зчитування даних
    athlete_results_df = spark.read.format('jdbc').options(
        url=db_config["url"],
        driver=db_config["driver"],
        dbtable="athlete_event_results",
        user=db_config["username"],
        password=db_config["password"]
    ).load()

    # Ініціалізація Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    # Відправка даних у Kafka топік
    for row in athlete_results_df.collect():
        value = row.asDict()
        producer.send(ATHLETE_TOPIC_NAME, value)
        print(f"Message sent to topic {ATHLETE_TOPIC_NAME}: {value} successfully.")
    producer.close()

# Функція для обробки стриму
def process_stream():
    schema = StructType([
        StructField("athlete_id", StringType(), True),
        StructField("sport", StringType(), True),
        StructField("medal", StringType(), True),
        StructField("event", StringType(), True),
        StructField("result", DoubleType(), True)
    ])

    # Читання з Kafka
    athlete_stream = spark.readStream.format("kafka").options(
        **{
            "kafka.bootstrap.servers": KAFKA_SERVERS,
            "subscribe": ATHLETE_TOPIC_NAME,
            "startingOffsets": "earliest",
            "failOnDataLoss": "false"
        }
    ).load()

    # Конвертація JSON у DataFrame
    athlete_results_parsed = athlete_stream.selectExpr("CAST(value AS STRING)").select(
        from_json(col("value"), schema).alias("data")
    ).select("data.*")

    # Зчитування фізичних даних атлетів
    athlete_bio_df = read_athlete_bio()
    filtered_bio_df = filter_invalid_data(athlete_bio_df)

    # Об'єднання даних
    joined_df = athlete_results_parsed.join(filtered_bio_df, "athlete_id")

    # Агрегація
    aggregated_df = joined_df.groupBy("sport", "medal", "sex", "country_noc").agg(
        avg("height").alias("avg_height"),
        avg("weight").alias("avg_weight")
    ).withColumn("timestamp", current_timestamp())

    # Запис у Kafka та MySQL
    def foreach_batch_function(batch_df, batch_id):
        # Запис у Kafka
        batch_df.selectExpr("to_json(struct(*)) AS value").write \
            .format("kafka") \
            .option("kafka.bootstrap.servers", ",".join(kafka_config["bootstrap_servers"])) \
            .option("topic", OUTPUT_TOPIC_NAME) \
            .save()

        # Запис у MySQL
        batch_df.write.format("jdbc").options(
            url=db_config["output_db_url"],
            driver=db_config["driver"],
            dbtable=db_config["output_db"],
            user=db_config["username"],
            password=db_config["password"]
        ).mode("append").save()

    query = aggregated_df.writeStream \
        .outputMode("update") \
        .foreachBatch(foreach_batch_function) \
        .start()

    query.awaitTermination()

# Запуск функцій паралельно
if __name__ == "__main__":
    # Запуск відправки даних у Kafka в окремому потоці
    producer_thread = Thread(target=send_to_kafka)
    producer_thread.start()

    # Запуск обробки стриму
    process_stream()

    # Очікування завершення потоку
    producer_thread.join()
