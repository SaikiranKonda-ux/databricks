# Vector Index Creation: Two Approaches

## Problem: Auto-Job Permission Failures

When using Delta Sync with managed embeddings, Databricks creates a background job that:
- Reads from source Delta table
- Calls embedding model endpoint
- Writes to vector index

**This job often fails with permission errors** in restricted environments.

---

## Approach 1: Managed Embeddings (Original)

**File:** `notebooks/01_setup/01_load_sample_data.py`

```python
client.create_delta_sync_index(
    endpoint_name="dev_support_ep",
    index_name="ts_dlh_dev_catalog.assets.kb_vs_index",
    source_table_name="ts_dlh_dev_catalog.assets.ticket_embeddings",
    pipeline_type="TRIGGERED",
    primary_key="ticket_id",
    embedding_source_column="content",  # Databricks computes embeddings
    embedding_model_endpoint_name="databricks-bge-large-en"  # Foundation Model API
)
```

**Pros:**
- ✅ Learn Model Serving Endpoint UI
- ✅ Databricks-managed infrastructure
- ✅ Automatic embedding updates

**Cons:**
- ❌ Requires Foundation Model API access
- ❌ Auto-job needs special permissions
- ❌ Costs per embedding request
- ❌ Job can fail silently

**Use when:**
- You have workspace admin access
- Foundation Model APIs enabled
- Production environment with proper IAM setup

---

## Approach 2: Manual Embeddings (Recommended for Learning)

**File:** `notebooks/01_setup/02_manual_embeddings_local_model.py`

```python
# Step 1: Compute embeddings in notebook
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)

# Step 2: Save to Delta with embeddings column
embeddings_df.write.saveAsTable("ticket_embeddings_manual")

# Step 3: Create Direct Vector Access index
client.create_delta_sync_index(
    endpoint_name="dev_support_ep",
    index_name="ts_dlh_dev_catalog.assets.kb_vs_index",
    source_table_name="ticket_embeddings_manual",
    pipeline_type="TRIGGERED",
    primary_key="ticket_id",
    embedding_dimension=384,
    embedding_vector_column="embedding"  # Pre-computed embeddings
)
```

**Pros:**
- ✅ No auto-job permission issues
- ✅ Uses notebook cluster (your permissions)
- ✅ Free embeddings (open-source model)
- ✅ Full control over embedding process
- ✅ Can still learn Vector Search UI

**Cons:**
- ❌ Manual embedding updates needed
- ❌ Don't experience Model Serving Endpoint UI
- ❌ Smaller embedding dimension (384 vs 768)

**Use when:**
- Permission issues with auto-jobs
- Budget-conscious personal learning
- Need full control over embedding process
- Working in restricted environments

---

## Key Differences

| Feature | Managed Embeddings | Manual Embeddings |
|---------|-------------------|-------------------|
| **Auto-job** | Yes (can fail) | No (runs in notebook) |
| **Permissions** | Service principal | Your cluster permissions |
| **Cost** | Pay per embedding | Free (local compute) |
| **Model** | databricks-bge-large-en (768d) | all-MiniLM-L6-v2 (384d) |
| **Updates** | Automatic via CDF | Manual re-run |
| **Learning** | Model Serving UI ✅ | Vector Search UI only |

---

## Recommendation

**For this learning project:**
1. **First try Approach 1** (Managed Embeddings) to experience full Databricks workflow
2. **If permission errors occur**, switch to **Approach 2** (Manual Embeddings)
3. Both approaches teach Vector Search, HNSW algorithm, and similarity search

**For production:**
- Use Approach 1 with proper IAM/permissions setup
- Automatic updates via Change Data Feed
- Enterprise-grade infrastructure
