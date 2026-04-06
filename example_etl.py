from pyspark.sql import functions as F

from spark_session import get_spark

spark = get_spark()

# Extract
print("Reading source table...")
df = spark.read.table("samples.nyctaxi.trips")
print(f"Row count: {df.count()}")

# Transform
result = (
    df.withColumn("trip_year", F.year("tpep_pickup_datetime"))
    .groupBy("trip_year", "vendor_id")
    .agg(
        F.count("*").alias("total_trips"),
        F.avg("trip_distance").alias("avg_distance"),
    )
    .orderBy("trip_year", "vendor_id")
)

# Load — print or write to a table
result.show(50)
print("ETL complete!")
