# Databricks notebook source
# MAGIC %md
# MAGIC # Topic 1: Vector DB - HNSW Algorithm & Similarity Search
# MAGIC
# MAGIC **UI Path**: Workspace → Machine Learning → Vector Search → Endpoints → dev_support_ep
# MAGIC
# MAGIC **View Index**: Catalog → ts_dlh_dev_catalog → assets → kb_vs_index
# MAGIC
# MAGIC **Documentation**:
# MAGIC - [Vector Search Overview](https://docs.databricks.com/aws/en/vector-search/vector-search)
# MAGIC - [Query Vector Index](https://docs.databricks.com/aws/en/vector-search/query-vector-search)
# MAGIC - [HNSW Algorithm Details](https://community.databricks.com/t5/generative-ai/databricks-vector-search-algorithm/td-p/142623)

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
VECTOR_ENDPOINT = "dev_support_ep"
VECTOR_INDEX = "kb_vs_index"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.{VECTOR_INDEX}"

client = VectorSearchClient()

# COMMAND ----------

index = client.get_index(name=VECTOR_INDEX_FQN)

index_info = index.describe()
print(f"Index: {index_info['name']}")
print(f"Status: {index_info.get('status', {}).get('state', 'UNKNOWN')}")
print(f"Endpoint: {index_info['endpoint_name']}")
print(f"Primary key: {index_info['primary_key']}")
print(f"Embedding model: {index_info.get('embedding_model_endpoint_name', 'N/A')}")

# COMMAND ----------

query_text = "My payment failed and I need help"

results = index.similarity_search(
    query_text=query_text,
    columns=["ticket_id", "content"],
    num_results=5
)

print(f"Query: {query_text}\n")
print("Top 5 similar documents:")
for idx, result in enumerate(results['result']['data_array'], 1):
    print(f"\n{idx}. Ticket ID: {result[0]}")
    print(f"   Content: {result[1][:200]}...")
    print(f"   Score: {results['result'].get('scores', [0]*5)[idx-1]}")

# COMMAND ----------

queries = [
    "App crashes on iPhone",
    "Cannot login to my account",
    "Need refund for subscription",
    "How to use API integration"
]

for query in queries:
    results = index.similarity_search(
        query_text=query,
        columns=["ticket_id"],
        num_results=3
    )
    print(f"\nQuery: {query}")
    print(f"Top matches: {[r[0] for r in results['result']['data_array']]}")

# COMMAND ----------

spark.sql(f"SELECT COUNT(*) as total_vectors FROM {CATALOG}.{SCHEMA_AI}.ticket_embeddings").show()

print(f"Vector Index: {VECTOR_INDEX_FQN}")
print(f"Algorithm: HNSW (Hierarchical Navigable Small World)")
print(f"Distance Metric: L2 (Euclidean)")
print(f"Embedding Model: databricks-bge-large-en (768 dimensions)")
