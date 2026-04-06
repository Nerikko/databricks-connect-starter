import os

from databricks.connect import DatabricksSession
from dotenv import load_dotenv


def get_spark():
    load_dotenv()
    builder = DatabricksSession.builder
    cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
    if cluster_id:
        builder = builder.clusterId(cluster_id)
    else:
        builder = builder.serverless(True)
    return builder.getOrCreate()
