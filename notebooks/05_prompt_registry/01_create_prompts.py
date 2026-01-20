# Databricks notebook source

import mlflow
from mlflow.prompts import register

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

registered_prompt = register(
    prompt=classify_ticket_prompt,
    name=prompt_name,
    params=["ticket_text"]
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

registered_prompt = register(
    prompt=extract_entities_prompt,
    name=prompt_name,
    params=["ticket_text"]
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

registered_prompt = register(
    prompt=generate_solution_prompt,
    name=prompt_name,
    params=["ticket_text", "category", "kb_content"]
)

print(f"Registered: {prompt_name}")

# COMMAND ----------

from mlflow.prompts import get_prompt

classify_prompt = get_prompt(f"{PROMPT_FQN}.classify_ticket_prompt")

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
