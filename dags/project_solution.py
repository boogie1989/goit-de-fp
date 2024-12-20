from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from config import SUFFIX
import datetime
import pendulum
from airflow.operators.bash import BashOperator

# --------------------------------------------
# Default Arguments for DAG
# --------------------------------------------
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --------------------------------------------
# Define DAG
# --------------------------------------------
with DAG(
    dag_id=f'{SUFFIX}_data_lake_pipeline',
    default_args=default_args,
    description='End-to-End Batch Data Lake Pipeline',
    schedule=None,
    start_date=pendulum.now('UTC'),
    catchup=False,
    tags=[SUFFIX]
) as dag:

    # --------------------------------------------
    # Task 1: Run landing_to_bronze.py Spark job
    # --------------------------------------------
    landing_to_bronze = SparkSubmitOperator(
        task_id='landing_to_bronze',
        name='landing_to_bronze',
        application='/opt/airflow/dags/landing_to_bronze.py', 
        conn_id='spark_local', 
        verbose=True,
        conf={
            'spark.master': 'local[*]'
        },
        dag=dag,
    )

    # --------------------------------------------
    # Task 2: Run bronze_to_silver.py Spark job
    # --------------------------------------------
    bronze_to_silver = SparkSubmitOperator(
        task_id='bronze_to_silver',
        name='bronze_to_silver',
        application='/opt/airflow/dags/bronze_to_silver.py',
        conn_id='spark_local', 
        verbose=True,
        conf={
            'spark.master': 'local[*]'  
        },
        dag=dag,
    )

    # --------------------------------------------
    # Task 3: Run silver_to_gold.py Spark job
    # --------------------------------------------
    silver_to_gold = SparkSubmitOperator(
        task_id='silver_to_gold',
        name='silver_to_gold',
        application='/opt/airflow/dags/silver_to_gold.py',
        conn_id='spark_local',
        verbose=True,
        conf={
            'spark.master': 'local[*]'
        },
        dag=dag,
    )

    # Define Task Dependencies
    landing_to_bronze >> bronze_to_silver >> silver_to_gold




