# Databricks notebook source
# MAGIC %md
# MAGIC # Manual Embeddings with Local Model (Bypass Permission Issues)
# MAGIC
# MAGIC **Problem**: Delta Sync with managed embeddings creates auto-job → fails due to permissions
# MAGIC
# MAGIC **Solution**: Compute embeddings in notebook cluster → Create Direct Vector Access index
# MAGIC
# MAGIC **Benefits**:
# MAGIC - ✅ No auto-job permission issues
# MAGIC - ✅ Use notebook cluster (your permissions)
# MAGIC - ✅ Free embeddings (sentence-transformers)
# MAGIC - ✅ Full control over embedding process

# COMMAND ----------

# MAGIC %pip install sentence-transformers==2.2.2 --quiet
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

from sentence_transformers import SentenceTransformer
from databricks.vector_search.client import VectorSearchClient
import pyspark.sql.functions as F

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_DATA = "data"
SCHEMA_AI = "assets"
VECTOR_ENDPOINT = "dev_support_ep"
VECTOR_INDEX = "kb_vs_index"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.{VECTOR_INDEX}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Download Model to Volume (One-time)

# COMMAND ----------

model_path = f"/Volumes/{CATALOG}/{SCHEMA_AI}/models/all-MiniLM-L6-v2"

try:
    model = SentenceTransformer(model_path)
    print(f"✅ Model loaded from volume: {model_path}")
except:
    print(f"📥 Downloading model (one-time, ~80MB)...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    model.save(model_path)
    print(f"✅ Model saved to volume: {model_path}")

print(f"Embedding dimension: {model.get_sentence_embedding_dimension()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Compute Embeddings in Notebook

# COMMAND ----------

source_df = spark.table(f"{CATALOG}.{SCHEMA_AI}.ticket_embeddings")
print(f"Source records: {source_df.count()}")

texts = [row.content for row in source_df.select("content").collect()]
ticket_ids = [row.ticket_id for row in source_df.select("ticket_id").collect()]

print(f"Computing embeddings for {len(texts)} documents...")
embeddings = model.encode(texts, show_progress_bar=True)

print(f"✅ Embeddings computed: {embeddings.shape}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Delta Table with Pre-computed Embeddings

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType, ArrayType, FloatType

embeddings_data = [
    (ticket_id, text, embedding.tolist())
    for ticket_id, text, embedding in zip(ticket_ids, texts, embeddings)
]

schema = StructType([
    StructField("ticket_id", StringType(), False),
    StructField("content", StringType(), False),
    StructField("embedding", ArrayType(FloatType()), False)
])

embeddings_df = spark.createDataFrame(embeddings_data, schema)

table_name = f"{CATALOG}.{SCHEMA_AI}.ticket_embeddings_manual"
embeddings_df.write.format("delta").mode("overwrite").saveAsTable(table_name)

print(f"✅ Table created: {table_name}")
print(f"Records: {embeddings_df.count()}")

# COMMAND ----------

spark.sql(f"""
ALTER TABLE {table_name}
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

print(f"✅ Change Data Feed enabled on {table_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Direct Vector Access Index (No Auto-Job)

# COMMAND ----------

client = VectorSearchClient()

try:
    endpoint = client.get_endpoint(VECTOR_ENDPOINT)
    print(f"✅ Endpoint ready: {endpoint['endpoint_status']['state']}")
except Exception as e:
    print(f"❌ Endpoint error: {str(e)}")
    print(f"Create endpoint first: Machine Learning → Vector Search → Create Endpoint → {VECTOR_ENDPOINT}")
    dbutils.notebook.exit("Endpoint not ready")

# COMMAND ----------

try:
    existing = client.get_index(name=VECTOR_INDEX_FQN)
    client.delete_index(name=VECTOR_INDEX_FQN)
    print(f"🗑️ Deleted existing index")
except:
    pass

index = client.create_delta_sync_index(
    endpoint_name=VECTOR_ENDPOINT,
    index_name=VECTOR_INDEX_FQN,
    source_table_name=table_name,
    pipeline_type="TRIGGERED",
    primary_key="ticket_id",
    embedding_dimension=384,
    embedding_vector_column="embedding"
)

print(f"✅ Direct Vector Access index created: {VECTOR_INDEX_FQN}")
print(f"   Source: {table_name}")
print(f"   Embedding column: embedding (pre-computed)")
print(f"   No auto-job needed - uses your notebook permissions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Sync and Verify

# COMMAND ----------

import time

print("🔄 Triggering sync...")
index.sync()

print("⏳ Waiting for sync to complete...")
for i in range(30):
    status = client.get_index(VECTOR_INDEX_FQN).describe()
    state = status.get('status', {}).get('state', 'UNKNOWN')
    print(f"   [{i+1}/30] State: {state}")

    if state == "ONLINE":
        print(f"✅ Index ONLINE and ready")
        break

    time.sleep(10)
else:
    print(f"⚠️ Index not ready after 5 minutes - check status in UI")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Test Query

# COMMAND ----------

index = client.get_index(name=VECTOR_INDEX_FQN)

query_text = "My payment failed and I need help"

query_embedding = model.encode([query_text])[0].tolist()

results = index.similarity_search(
    query_vector=query_embedding,
    columns=["ticket_id", "content"],
    num_results=3
)

print(f"Query: {query_text}\n")
print("Top 3 matches:")
for idx, result in enumerate(results['result']['data_array'], 1):
    print(f"{idx}. {result[0]}: {result[1][:100]}...")

# COMMAND ----------

print("\n✅ Manual Embedding Setup Complete:")
print(f"   Model: sentence-transformers/all-MiniLM-L6-v2 (384 dim)")
print(f"   Table: {table_name} (with pre-computed embeddings)")
print(f"   Index: {VECTOR_INDEX_FQN} (Direct Vector Access)")
print(f"   Permissions: Uses notebook cluster (your permissions)")
print(f"   Cost: Free embeddings, pay only for vector endpoint")
