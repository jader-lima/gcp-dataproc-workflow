import argparse
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame


def create_spark_session(app_name):
    spark_packages_list = [
        'io.delta:delta-core_2.12:2.3.0',
        'io.delta:delta-storage-2.3.0'
    ]
    #2.2.x
    spark_packages = ",".join(spark_packages_list)

    return SparkSession \
        .builder \
        .appName(app_name) \
        .master("local[3]") \
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true")\
        .config("spark.jars.packages", spark_packages) \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.databricks.delta.schema.autoMerge.enabled","true") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .enableHiveSupport()\
        .getOrCreate()


def read_csv_file(spark,path_transient:str):
    return spark.read.format('csv')\
    .option("header", True)\
    .option("sep", ",")\
    .option("quote","\'")\
    .option("inferSchema",True)\
    .load(path_transient)

def write_delta_file(path_bronze:str,df:DataFrame):
    df.write.format('delta').mode('overwrite').save(path_bronze )

def main(app_name, transient_zone, bronze_zone ):
    spark = create_spark_session(app_name)
    df_csv = read_csv_file(spark, transient_zone)
    write_delta_file(bronze_zone, df_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--app_name',
        type=str,
        dest='app_name',
        required=True,
        help='Pyspark Application Name')

    parser.add_argument(
        '--bucket_transient',
        type=str,
        dest='bucket_transient',
        required=True,
        help='URI of the GCS transient bucket')

    parser.add_argument(
        '--bucket_bronze',
        type=str,
        dest='bucket_bronze',
        required=True,
        help='URI of the GCS bronze bucket')

        

    known_args, pipeline_args = parser.parse_known_args()
    main(known_args.app_name, known_args.bucket_transient, known_args.bucket_bronze)