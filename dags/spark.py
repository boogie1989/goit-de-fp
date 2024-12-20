from pyspark.sql import SparkSession

def create_spark_session(name):
    return SparkSession.builder.appName(name).master("local[*]").getOrCreate()  