#!/usr/bin/env bash

set -euo pipefail

JOB_NAME="databricks-connect-starter-job"
DBFS_BASE_PATH="dbfs:/apps/databricks-connect-starter"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <CLUSTER_ID>"
  echo "Exemplo: $0 1234-567890-abcd123"
  exit 1
fi

CLUSTER_ID="$1"

echo "Verificando autenticação Databricks CLI..."
databricks auth env >/dev/null

echo "Copiando scripts para o DBFS..."
databricks fs mkdirs "$DBFS_BASE_PATH"
databricks fs cp example_query.py "${DBFS_BASE_PATH}/example_query.py" --overwrite
databricks fs cp example_etl.py   "${DBFS_BASE_PATH}/example_etl.py"   --overwrite

echo "Criando Job '${JOB_NAME}' com 2 tasks..."

databricks jobs create --json "{
  \"name\": \"${JOB_NAME}\",
  \"tasks\": [
    {
      \"task_key\": \"example_query\",
      \"spark_python_task\": {
        \"python_file\": \"${DBFS_BASE_PATH}/example_query.py\"
      },
      \"existing_cluster_id\": \"${CLUSTER_ID}\"
    },
    {
      \"task_key\": \"example_etl\",
      \"depends_on\": [
        { \"task_key\": \"example_query\" }
      ],
      \"spark_python_task\": {
        \"python_file\": \"${DBFS_BASE_PATH}/example_etl.py\"
      },
      \"existing_cluster_id\": \"${CLUSTER_ID}\"
    }
  ]
}"

echo "Job criado. Veja em Workflows > Jobs no workspace Databricks."

