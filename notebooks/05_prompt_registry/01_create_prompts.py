# Databricks notebook source
# MAGIC %md
# MAGIC # Topic 4: Prompt Registry - Management & Versioning
# MAGIC
# MAGIC **UI Path**: Workspace → Machine Learning → Experiments → [Experiment] → Prompts tab
# MAGIC
# MAGIC **View Prompts**: Catalog → ts_dlh_dev_catalog → assets → Prompts (Functions)
# MAGIC
# MAGIC **Documentation**:
# MAGIC - [Prompt Registry Overview](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/)
# MAGIC - [Create and Edit Prompts](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts)
# MAGIC - [Use Prompts in Apps](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps)

# COMMAND ----------

import mlflow

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
PROMPT_FQN = f"{CATALOG}.{SCHEMA_AI}"

# COMMAND ----------

classify_ticket_prompt = """You are a support ticket classifier.

Analyze the following ticket and classify it:

Ticket: {ticket_text}

Provide:
1. Priority (low/medium/high/urgent)
2. Category (billing/account/technical/product)
3. Sentiment (positive/neutral/negative)
4. Recommended Team

Output as JSON."""

prompt_name = f"{PROMPT_FQN}.classify_ticket_prompt"

registered_prompt = mlflow.genai.register_prompt(
    name=prompt_name,
    template=classify_ticket_prompt,
    commit_message="Initial version for ticket classification"
)

print(f"Registered: {prompt_name}")
print(f"Version: {registered_prompt.version}")

# COMMAND ----------

extract_entities_prompt = """Extract key entities from the support ticket.

Ticket: {ticket_text}

Extract:
- Customer ID
- Order ID
- Error codes
- Product names
- Dates mentioned

Output as JSON with keys: customer_id, order_id, error_codes, products, dates."""

prompt_name = f"{PROMPT_FQN}.extract_entities_prompt"

registered_prompt = mlflow.genai.register_prompt(
    name=prompt_name,
    template=extract_entities_prompt,
    commit_message="Entity extraction prompt"
)

print(f"Registered: {prompt_name}")

# COMMAND ----------

generate_solution_prompt = """You are a support agent providing solutions.

Ticket: {ticket_text}
Category: {category}
Related KB: {kb_content}

Generate a helpful solution response that:
1. Acknowledges the issue
2. Provides step-by-step solution
3. References KB article if relevant
4. Offers next steps

Keep response concise and professional."""

prompt_name = f"{PROMPT_FQN}.generate_solution_prompt"

registered_prompt = mlflow.genai.register_prompt(
    name=prompt_name,
    template=generate_solution_prompt,
    commit_message="Solution generation prompt with KB context"
)

print(f"Registered: {prompt_name}")

# COMMAND ----------

classify_prompt = mlflow.genai.get_prompt(f"{PROMPT_FQN}.classify_ticket_prompt")

test_ticket = "My payment failed and I need urgent help"
formatted = classify_prompt.format(ticket_text=test_ticket)

print("Prompt Template Test:")
print(formatted)

# COMMAND ----------

print("\nPrompts registered in Unity Catalog:")
print(f"  1. {PROMPT_FQN}.classify_ticket_prompt")
print(f"  2. {PROMPT_FQN}.extract_entities_prompt")
print(f"  3. {PROMPT_FQN}.generate_solution_prompt")
print(f"\nView in UI: Catalog → {CATALOG} → {SCHEMA_AI} → Prompts")
