# Databricks notebook source
# MAGIC %md
# MAGIC # Prerequisites Setup - Customer Support AI System
# MAGIC
# MAGIC **Purpose**: Create Unity Catalog infrastructure for learning AI Applications
# MAGIC
# MAGIC **Use Case**: Customer Support Ticket Intelligence System using:
# MAGIC - Vector Search for semantic similarity
# MAGIC - AI Agents (single & multi-agent)
# MAGIC - MLflow for tracking
# MAGIC - Unity Catalog for governance
# MAGIC - Azure OpenAI for LLM capabilities
# MAGIC
# MAGIC **Repository**: Based on https://github.com/bigdatavik/databricks-ai-ticket-vectorsearch

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration
# MAGIC
# MAGIC Define naming conventions following pattern: `{env}_{domain}.{purpose}.{entity}`

# COMMAND ----------

# Configuration
CATALOG = "ts_dlh_dev_catalog"
SCHEMA_DATA = "data"
SCHEMA_AI = "assets"
VOLUME_NAME = "kb_docs_volume"
VECTOR_ENDPOINT = "dev_support_ep"
VECTOR_INDEX = "kb_vs_index"

# Full qualified names
SCHEMA_DATA_FQN = f"{CATALOG}.{SCHEMA_DATA}"
SCHEMA_AI_FQN = f"{CATALOG}.{SCHEMA_AI}"
VOLUME_FQN = f"{CATALOG}.{SCHEMA_DATA}.{VOLUME_NAME}"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.{VECTOR_INDEX}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Catalog
# MAGIC
# MAGIC **Catalog**: `ts_dlh_dev_catalog`
# MAGIC - Team Standard: ts_dlh (Team Data Lakehouse)
# MAGIC - Environment: Development

# COMMAND ----------

spark.sql(f"""
CREATE CATALOG IF NOT EXISTS {CATALOG}
COMMENT 'AI Applications Learning Environment - Customer Support Ticket Intelligence'
""")

print(f"✅ Catalog created: {CATALOG}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Schemas
# MAGIC
# MAGIC **Two schemas** (simplified, no medallion architecture):
# MAGIC 1. `data` - Store tickets and knowledge base
# MAGIC 2. `assets` - Vector indexes, models, agents, functions, prompts

# COMMAND ----------

# Schema 1: Data
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {SCHEMA_DATA_FQN}
COMMENT 'Support tickets and knowledge base documents'
""")

print(f"✅ Schema created: {SCHEMA_DATA_FQN}")

# COMMAND ----------

# Schema 2: AI Assets
spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {SCHEMA_AI_FQN}
COMMENT 'Vector indexes, ML models, AI agents, UC functions, and prompt templates'
""")

print(f"✅ Schema created: {SCHEMA_AI_FQN}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Volume
# MAGIC
# MAGIC **Volume**: Store PDF/text documents for ai_parse_document

# COMMAND ----------

spark.sql(f"""
CREATE VOLUME IF NOT EXISTS {VOLUME_FQN}
COMMENT 'Storage for PDF/text knowledge base documents'
""")

print(f"✅ Volume created: {VOLUME_FQN}")
print(f"📁 Volume path: /Volumes/{CATALOG}/{SCHEMA_DATA}/{VOLUME_NAME}/")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Tables
# MAGIC
# MAGIC **3 tables** focused on AI use cases:
# MAGIC 1. `tickets` - Support ticket data
# MAGIC 2. `kb_documents` - Knowledge base documents
# MAGIC 3. `ticket_embeddings` - Embeddings for Vector Search

# COMMAND ----------

# MAGIC %md
# MAGIC ### Table 1: Support Tickets

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_DATA_FQN}.tickets (
  ticket_id STRING NOT NULL COMMENT 'Unique ticket identifier',
  ticket_text STRING COMMENT 'Full ticket description for agents to process',
  subject STRING COMMENT 'Ticket subject line',
  customer_id STRING COMMENT 'Customer identifier',
  created_timestamp TIMESTAMP COMMENT 'Ticket creation time',
  source STRING COMMENT 'Channel: email, chat, phone, web'
)
USING DELTA
COMMENT 'Customer support tickets for AI agent classification and routing'
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")

print(f"✅ Table created: {SCHEMA_DATA_FQN}.tickets")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Table 2: Knowledge Base Documents

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_DATA_FQN}.kb_documents (
  doc_id STRING NOT NULL COMMENT 'Unique document identifier',
  doc_name STRING COMMENT 'Document name/title',
  content STRING COMMENT 'Document text for embedding and RAG',
  category STRING COMMENT 'Document category: troubleshooting, policy, runbook',
  created_timestamp TIMESTAMP COMMENT 'Document ingestion time'
)
USING DELTA
COMMENT 'Knowledge base documents for RAG and vector search'
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")

print(f"✅ Table created: {SCHEMA_DATA_FQN}.kb_documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Table 3: Ticket Embeddings (for Vector Search)

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SCHEMA_AI_FQN}.ticket_embeddings (
  ticket_id STRING NOT NULL COMMENT 'Primary key for vector index',
  content STRING COMMENT 'Text to embed (Databricks auto-generates embeddings)',
  created_timestamp TIMESTAMP COMMENT 'Embedding creation time'
)
USING DELTA
COMMENT 'Embeddings table for Databricks Vector Search with managed embeddings'
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")

print(f"✅ Table created: {SCHEMA_AI_FQN}.ticket_embeddings")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Create Vector Search Endpoint
# MAGIC
# MAGIC **Note**: Endpoint creation requires Databricks SDK

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# Check if endpoint exists
try:
    existing_endpoint = client.get_endpoint(name=VECTOR_ENDPOINT)
    print(f"ℹ️  Vector Search endpoint already exists: {VECTOR_ENDPOINT}")
    print(f"   Status: {existing_endpoint.get('endpoint_status', {}).get('state', 'Unknown')}")
except Exception as e:
    # Create endpoint if it doesn't exist
    print(f"Creating Vector Search endpoint: {VECTOR_ENDPOINT}")
    client.create_endpoint(
        name=VECTOR_ENDPOINT,
        endpoint_type="STANDARD"
    )
    print(f"✅ Vector Search endpoint created: {VECTOR_ENDPOINT}")
    print(f"⏳ Endpoint is provisioning... (may take 5-10 minutes)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Create Vector Search Index
# MAGIC
# MAGIC **Requirements**:
# MAGIC - Endpoint must be in `ONLINE` state
# MAGIC - Source table must have data (will add in next notebook)
# MAGIC
# MAGIC **Note**: This step will be executed after loading sample data

# COMMAND ----------

# Check endpoint status
try:
    endpoint_info = client.get_endpoint(name=VECTOR_ENDPOINT)
    endpoint_state = endpoint_info.get('endpoint_status', {}).get('state', 'Unknown')

    print(f"Vector Search Endpoint: {VECTOR_ENDPOINT}")
    print(f"Status: {endpoint_state}")

    if endpoint_state == "ONLINE":
        print("✅ Endpoint is ready for index creation")
        print("\n📝 Next step: Run notebook to load sample data, then create vector index")
    else:
        print(f"⏳ Endpoint is not ready yet. Current state: {endpoint_state}")
        print("   Please wait for endpoint to reach ONLINE state before creating index")

except Exception as e:
    print(f"⚠️  Could not check endpoint status: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Vector Index Creation (Execute after data load)
# MAGIC
# MAGIC ```python
# MAGIC # This will be executed in a later notebook after loading data
# MAGIC client.create_delta_sync_index(
# MAGIC     endpoint_name=VECTOR_ENDPOINT,
# MAGIC     index_name=VECTOR_INDEX_FQN,
# MAGIC     source_table_name=f"{SCHEMA_AI_FQN}.ticket_embeddings",
# MAGIC     pipeline_type="TRIGGERED",
# MAGIC     primary_key="ticket_id",
# MAGIC     embedding_source_column="content",
# MAGIC     embedding_model_endpoint_name="databricks-bge-large-en"
# MAGIC )
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary of Created Resources
# MAGIC
# MAGIC | Resource Type | Name | Purpose |
# MAGIC |--------------|------|---------|
# MAGIC | **Catalog** | `ts_dlh_dev_catalog` | Root namespace for all AI resources |
# MAGIC | **Schema** | `ts_dlh_dev_catalog.data` | Tickets and knowledge base storage |
# MAGIC | **Schema** | `ts_dlh_dev_catalog.assets` | AI models, agents, functions, indexes |
# MAGIC | **Volume** | `ts_dlh_dev_catalog.data.kb_docs_volume` | PDF/document storage |
# MAGIC | **Table** | `ts_dlh_dev_catalog.data.tickets` | Support ticket data |
# MAGIC | **Table** | `ts_dlh_dev_catalog.data.kb_documents` | Knowledge base documents |
# MAGIC | **Table** | `ts_dlh_dev_catalog.assets.ticket_embeddings` | Embeddings for vector search |
# MAGIC | **Endpoint** | `dev_support_ep` | Vector Search endpoint (STANDARD) |
# MAGIC | **Index** | `ts_dlh_dev_catalog.assets.kb_vs_index` | Vector index (created after data load) |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. ✅ Prerequisites created (this notebook)
# MAGIC 2. 📝 Load sample ticket data
# MAGIC 3. 📝 Load knowledge base documents
# MAGIC 4. 📝 Create vector search index
# MAGIC 5. 📝 Begin AI topic learning:
# MAGIC    - Vector DB queries
# MAGIC    - MLflow tracking
# MAGIC    - Tracing
# MAGIC    - ai_parse_document
# MAGIC    - Prompt Registry
# MAGIC    - Tools Registry
# MAGIC    - Single Agent
# MAGIC    - Multi-Agent
# MAGIC    - Agent Bricks
# MAGIC    - Playground & Serving
# MAGIC    - MCP
# MAGIC    - App Services

# COMMAND ----------

print("=" * 60)
print("🎉 Prerequisites Setup Complete!")
print("=" * 60)
print(f"\n📦 Created Resources:")
print(f"   - Catalog: {CATALOG}")
print(f"   - Schemas: {SCHEMA_DATA}, {SCHEMA_AI}")
print(f"   - Tables: 3 (tickets, kb_documents, ticket_embeddings)")
print(f"   - Volume: {VOLUME_NAME}")
print(f"   - Vector Endpoint: {VECTOR_ENDPOINT}")
print(f"\n📁 Volume Path: /Volumes/{CATALOG}/{SCHEMA_DATA}/{VOLUME_NAME}/")
print(f"\n🚀 Ready for Topic 1: Vector DB")
