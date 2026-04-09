"""Simple test job — no external dependencies, runs on any Databricks cluster."""
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.sql("SELECT 'hello from test job' AS message, current_timestamp() AS ts")
df.show(truncate=False)

print("Test job completed successfully!")
