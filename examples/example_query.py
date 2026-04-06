from dbstarter import get_spark

spark = get_spark()

# Read a table — executes on Databricks, results come back here
df = spark.read.table("samples.nyctaxi.trips")
df.show(10)

# Run SQL
result = spark.sql("""
    SELECT vendor_id, COUNT(*) as trips, AVG(trip_distance) as avg_dist
    FROM samples.nyctaxi.trips
    GROUP BY vendor_id
""")
result.show()

# Pull data to local Python
for row in result.collect():
    print(f"Vendor {row.vendor_id}: {row.trips} trips")
