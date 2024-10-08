from pyspark.sql import SparkSession
from pyspark.sql import functions as F, Window
from pyspark.sql.types import StructField, StructType, StringType, IntegerType, BooleanType, TimestampType, LongType
import logging
import os

cur_dir = os.path.dirname(__file__)
log_dir = os.path.join(cur_dir,"logs")
os.makedirs(log_dir,exist_ok=1)
logger = logging.getLogger("spark_consumer")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler = logging.FileHandler(os.path.join(log_dir,"spark_logs.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():

    topic = "velib_data"
    client = "JCDecaux API"
    logger.debug(f"Receiving data from Kafka topic: {topic}, client: {client}")

    try:
        spark = SparkSession\
            .builder\
            .master("local[*]")\
            .appName('velib_stream_consumer')\
            .config("spark.sql.shuffle.partitions", 1)\
            .getOrCreate()
    except Exception as e:
        logger.error(e, exc_info=1)
    
    try:
        df = spark.readStream\
            .format("kafka")\
            .option("kafka.group.id", "streamspark")\
            .option("kafka.bootstrap.servers", "kafka:9092")\
            .option("subscribe", topic)\
            .option("startingOffsets", "latest")\
            .option("failOnDataLoss", "false")\
            .load()
    except Exception as e:
        logger.error(e, exc_info=1)

    schema = StructType(
        [StructField("number",IntegerType(),True),
        StructField("contract_name",StringType(),True),
        StructField("name",StringType(),True),
        StructField("address",StringType(),True),
        StructField("position",StringType(),True),
        StructField("banking",BooleanType(),True),
        StructField("bonus",BooleanType(),True),
        StructField("bike_stands",IntegerType(),True),
        StructField("available_bike_stands",IntegerType(),True),
        StructField("available_bikes",IntegerType(),True),
        StructField("status",StringType(),True),
        StructField("last_update",LongType(),True)])

    df = df.select(df.timestamp, F.explode(F.from_json(F.decode(df.value, "UTF-8"), "ARRAY<STRING>")).alias("val"))
    df = df.withColumn("val", F.from_json(df.val, schema=schema))
    df = df.select(df.timestamp, F.col("val.*"))
    df = df.filter(df.contract_name=="bruxelles").withColumn("last_update", (df.last_update/F.lit(1000)).cast(TimestampType()))

    def fetch_last(batch, id):
        w = Window.partitionBy(["number", "last_update"]).orderBy(F.col("last_update").desc())
        batch = batch.withColumn("rank", F.dense_rank().over(w)).filter("rank==1").dropDuplicates(["number","rank"])
        batch.write.format("csv").option("header", "true").mode("overwrite").save("file:///tmp/v_data")
        # batch.show()
        
    query = df \
        .writeStream \
        .foreachBatch(fetch_last)\
        .trigger(processingTime="2 minutes")\
        .start()\
        .awaitTermination()
    

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        logger.error(e, exc_info=True)
    except KeyboardInterrupt:
        print("spark terminating...")