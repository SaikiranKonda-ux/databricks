# Databricks notebook source
# MAGIC %md
# MAGIC # Single Agent: Ticket Classifier with RAG
# MAGIC
# MAGIC **UI Path**: Workspace → Machine Learning → Experiments → ticket-classifier-agent
# MAGIC
# MAGIC **View Traces**: Experiments → ticket-classifier-agent → Traces tab → Timeline view
# MAGIC
# MAGIC **Documentation**:
# MAGIC - [Author AI Agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent)
# MAGIC - [Agent Tutorial](https://docs.databricks.com/aws/en/generative-ai/tutorials/agent-framework-notebook)
# MAGIC - [Azure: Build Agent](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/tutorials/agent-framework-notebook)

# COMMAND ----------

import mlflow
import os
from databricks.vector_search.client import VectorSearchClient

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_DATA = "data"
SCHEMA_AI = "assets"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.kb_vs_index"

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

# COMMAND ----------

@mlflow.trace
def search_kb(query: str, num_results: int = 3) -> str:
    client = VectorSearchClient()
    index = client.get_index(name=VECTOR_INDEX_FQN)

    results = index.similarity_search(
        query_text=query,
        columns=["content"],
        num_results=num_results
    )

    kb_docs = [r[0] for r in results['result']['data_array']]
    return "\n\n".join(kb_docs)

# COMMAND ----------

@mlflow.trace
def classify_ticket(ticket_text: str) -> dict:
    kb_content = search_kb(ticket_text, num_results=2)

    prompt_template = mlflow.genai.get_prompt(f"{CATALOG}.{SCHEMA_AI}.classify_ticket_prompt")
    prompt = prompt_template.format(ticket_text=ticket_text)

    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    classification = response.choices[0].message.content

    return {
        "ticket": ticket_text,
        "classification": classification,
        "kb_used": kb_content[:200]
    }

# COMMAND ----------

test_tickets = [
    "My payment failed and I need urgent help",
    "Cannot login to my account",
    "How do I use the API integration?"
]

mlflow.set_experiment(f"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/ticket-classifier-agent")

for ticket in test_tickets:
    with mlflow.start_run(run_name=f"classify_{ticket[:20]}"):
        result = classify_ticket(ticket)

        mlflow.log_param("ticket", ticket)
        mlflow.log_dict(result, "classification_result.json")

        print(f"\nTicket: {ticket}")
        print(f"Result: {result['classification']}")

# COMMAND ----------

print("Single Agent Created: Ticket Classifier")
print(f"  - Uses Vector Search for KB retrieval")
print(f"  - Uses Prompt Registry for classification")
print(f"  - Traced with MLflow")
print(f"\nView traces: MLflow UI → Experiments → ticket-classifier-agent → Traces")
