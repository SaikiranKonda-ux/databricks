# Databricks notebook source

import mlflow
from databricks.vector_search.client import VectorSearchClient

mlflow.set_tracking_uri("databricks")
experiment_name = f"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/support-ai-tracing"
mlflow.set_experiment(experiment_name)

print(f"MLflow Experiment: {experiment_name}")
print(f"Tracing enabled: {mlflow.is_tracing_enabled()}")

# COMMAND ----------

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.kb_vs_index"

@mlflow.trace
def search_knowledge_base(query: str, num_results: int = 3) -> list:
    client = VectorSearchClient()
    index = client.get_index(name=VECTOR_INDEX_FQN)

    results = index.similarity_search(
        query_text=query,
        columns=["ticket_id", "content"],
        num_results=num_results
    )

    return results['result']['data_array']

# COMMAND ----------

with mlflow.start_run(run_name="vector_search_trace"):
    query = "Payment failed"
    results = search_knowledge_base(query, num_results=3)

    mlflow.log_param("query", query)
    mlflow.log_param("num_results", 3)
    mlflow.log_metric("results_returned", len(results))

    print(f"Query: {query}")
    print(f"Results: {len(results)}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")

# COMMAND ----------

queries = ["Login problem", "Subscription cancel", "API documentation"]

for query in queries:
    with mlflow.start_run(run_name=f"search_{query.replace(' ', '_')}"):
        results = search_knowledge_base(query)
        mlflow.log_param("query", query)
        mlflow.log_metric("results_count", len(results))
        print(f"Traced: {query}")

print(f"\nView traces: MLflow UI → {experiment_name} → Traces tab")
