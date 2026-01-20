# Setup Guide - Customer Support AI Learning System

## ✅ What You've Completed

Your Unity Catalog infrastructure is ready:
- ✅ Catalog: `ts_dlh_dev_catalog`
- ✅ Schemas: `data`, `assets`
- ✅ Tables: `tickets`, `kb_documents`, `ticket_embeddings`
- ✅ Volume: `kb_docs_volume`
- ✅ Vector Endpoint: `dev_support_ep`

---

## 📥 Data Sources - NO DOWNLOADS NEEDED!

**All sample data is generated in the notebook** - no external files required.

### What Gets Created:

1. **100 Support Tickets** (auto-generated)
   - Categories: billing, technical, account, product
   - Priorities: low, medium, high, urgent
   - Sources: email, chat, phone, web
   - Realistic ticket descriptions

2. **12 Knowledge Base Documents** (embedded in notebook)
   - Payment troubleshooting
   - Subscription management
   - Mobile app issues
   - Login problems
   - Performance optimization
   - Password reset
   - Security best practices
   - Data export guide
   - API integration
   - Error code reference
   - Support channels
   - Account deletion/privacy

3. **3 Text Files** (created in volume)
   - troubleshooting_guide.txt
   - security_best_practices.txt
   - onboarding_checklist.txt

---

## 🚀 Next Steps

### Step 1: Upload Notebooks to Databricks

1. Go to your Databricks workspace
2. Click **Workspace** → **Users** → your user folder
3. Create folder: `databricks-ai-learning`
4. Upload from your local repo:
   ```
   notebooks/01_setup/00_create_catalog_schema_prerequisites.py
   notebooks/01_setup/01_load_sample_data.py
   ```

### Step 2: Run Data Loading Notebook

1. Open `01_load_sample_data.py` in Databricks
2. Click **Run All**
3. Wait 5-10 minutes for:
   - Data generation
   - Table population
   - Vector index creation
   - Files uploaded to volume

### Step 3: Verify Everything Works

**Check Tables:**
```sql
SELECT COUNT(*) FROM ts_dlh_dev_catalog.data.tickets;          -- Should be 100
SELECT COUNT(*) FROM ts_dlh_dev_catalog.data.kb_documents;     -- Should be 12
SELECT COUNT(*) FROM ts_dlh_dev_catalog.assets.ticket_embeddings; -- Should be 12
```

**Check Volume Files:**
```python
dbutils.fs.ls("/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/")
# Should show 3 .txt files
```

**Check Vector Index:**
1. Go to **Machine Learning** → **Vector Search**
2. Find endpoint: `dev_support_ep`
3. Check status: Should be `ONLINE`
4. Find index: `ts_dlh_dev_catalog.assets.kb_vs_index`
5. Check sync status: Should be `ONLINE` (takes 2-5 minutes)

---

## 📂 File Upload Details

### Where Files Are Stored:
```
/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/
```

### How to Upload Additional Files (Optional):

**Method 1: Databricks UI**
1. Go to **Data** → **Volumes**
2. Navigate to: `ts_dlh_dev_catalog` → `data` → `kb_docs_volume`
3. Click **Upload Files**
4. Drag and drop PDF/DOCX/TXT files

**Method 2: In Notebook**
```python
# Upload file programmatically
dbutils.fs.put(
    "/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/my_file.pdf",
    file_contents,
    overwrite=True
)
```

**Method 3: CLI (if enabled)**
```bash
databricks fs cp local_file.pdf dbfs:/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/
```

---

## 🔍 What Each File Does

### `00_create_catalog_schema_prerequisites.py`
- Creates catalog, schemas, tables, volume, endpoint
- You already ran this (manually created these)
- Can skip or use as reference

### `01_load_sample_data.py` ⭐ **RUN THIS NEXT**
- Generates all sample data
- Populates tables
- Creates files in volume
- Creates vector index
- **This is your next step!**

---

## 🎯 After Data Loading

You'll be ready to start:

**Topic 1: Vector DB**
- Query the vector index
- Test similarity search
- Find relevant KB docs for tickets
- Understand vector embeddings

**Topics 2-12**: Continue through the learning path covering:
- MLflow tracking
- Tracing
- ai_parse_document
- Prompt registry
- Tools registry
- Single & multi-agent
- Agent Bricks
- Playground/Serving
- MCP
- App Services

---

## 🆘 Troubleshooting

**Vector endpoint stuck in PROVISIONING:**
- Wait 5-10 minutes
- Refresh the UI
- If > 15 minutes, contact Databricks support

**Vector index creation fails:**
- Check table has data: `SELECT COUNT(*) FROM ts_dlh_dev_catalog.assets.ticket_embeddings`
- Verify endpoint is ONLINE
- Check you have CREATE permissions on schema

**Cannot upload to volume:**
- Verify volume path is correct
- Check you have WRITE permissions
- Try using notebook upload method instead of UI

**Tables not showing data:**
- Re-run the data generation cells in notebook
- Check for error messages
- Verify catalog/schema names match

---

## 📞 Quick Reference

| Resource | Full Name |
|----------|-----------|
| Catalog | `ts_dlh_dev_catalog` |
| Data Schema | `ts_dlh_dev_catalog.data` |
| AI Schema | `ts_dlh_dev_catalog.assets` |
| Tickets Table | `ts_dlh_dev_catalog.data.tickets` |
| KB Table | `ts_dlh_dev_catalog.data.kb_documents` |
| Embeddings Table | `ts_dlh_dev_catalog.assets.ticket_embeddings` |
| Volume Path | `/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/` |
| Vector Endpoint | `dev_support_ep` |
| Vector Index | `ts_dlh_dev_catalog.assets.kb_vs_index` |

---

## 🎉 Summary

**You need to:**
1. ✅ Upload `01_load_sample_data.py` to Databricks
2. ✅ Run the notebook (Run All)
3. ✅ Wait for vector index sync (5 mins)
4. ✅ Start learning Topic 1: Vector DB

**No external downloads required** - everything is self-contained!

**Sources:**
- GitHub reference: https://github.com/bigdatavik/databricks-ai-ticket-vectorsearch
- Databricks Vector Search docs: https://docs.databricks.com/en/generative-ai/vector-search
