# Databricks notebook source

import mlflow
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from databricks.vector_search.client import VectorSearchClient

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.kb_vs_index"

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

# COMMAND ----------

class AgentState(TypedDict):
    ticket: str
    category: str
    priority: int
    kb_results: str
    classification: str
    solution: str
    final_output: str

# COMMAND ----------

@mlflow.trace
def categorize_agent(state: AgentState) -> AgentState:
    ticket = state["ticket"]

    category_prompt = f"""Classify this ticket into one category: billing, account, technical, product

Ticket: {ticket}

Output only the category name."""

    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": category_prompt}],
        temperature=0
    )

    state["category"] = response.choices[0].message.content.strip().lower()
    return state

# COMMAND ----------

@mlflow.trace
def priority_agent(state: AgentState) -> AgentState:
    ticket = state["ticket"]

    priority_prompt = f"""Rate priority 1-4 (1=low, 4=urgent) based on keywords like urgent, critical, cannot, error.

Ticket: {ticket}

Output only the number."""

    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": priority_prompt}],
        temperature=0
    )

    state["priority"] = int(response.choices[0].message.content.strip())
    return state

# COMMAND ----------

@mlflow.trace
def retrieval_agent(state: AgentState) -> AgentState:
    client = VectorSearchClient()
    index = client.get_index(name=VECTOR_INDEX_FQN)

    results = index.similarity_search(
        query_text=state["ticket"],
        columns=["content"],
        num_results=2
    )

    kb_docs = [r[0] for r in results['result']['data_array']]
    state["kb_results"] = "\n".join(kb_docs)
    return state

# COMMAND ----------

@mlflow.trace
def solution_agent(state: AgentState) -> AgentState:
    solution_prompt = f"""Generate solution for:

Ticket: {state['ticket']}
Category: {state['category']}
Priority: {state['priority']}
KB: {state['kb_results'][:500]}

Provide clear solution steps."""

    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": solution_prompt}],
        temperature=0
    )

    state["solution"] = response.choices[0].message.content
    state["final_output"] = f"Category: {state['category']}, Priority: {state['priority']}\n\n{state['solution']}"
    return state

# COMMAND ----------

workflow = StateGraph(AgentState)

workflow.add_node("categorize", categorize_agent)
workflow.add_node("prioritize", priority_agent)
workflow.add_node("retrieve", retrieval_agent)
workflow.add_node("solve", solution_agent)

workflow.set_entry_point("categorize")
workflow.add_edge("categorize", "prioritize")
workflow.add_edge("prioritize", "retrieve")
workflow.add_edge("retrieve", "solve")
workflow.add_edge("solve", END)

graph = workflow.compile()

# COMMAND ----------

mlflow.set_experiment(f"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/multi-agent-supervisor")

test_ticket = "My payment failed and I need urgent help"

with mlflow.start_run(run_name="multi_agent_test"):
    initial_state = {
        "ticket": test_ticket,
        "category": "",
        "priority": 0,
        "kb_results": "",
        "classification": "",
        "solution": "",
        "final_output": ""
    }

    final_state = graph.invoke(initial_state)

    mlflow.log_param("ticket", test_ticket)
    mlflow.log_param("category", final_state["category"])
    mlflow.log_param("priority", final_state["priority"])
    mlflow.log_text(final_state["final_output"], "solution.txt")

    print(f"Ticket: {test_ticket}")
    print(f"\n{final_state['final_output']}")

# COMMAND ----------

print("\nMulti-Agent System Created:")
print("  1. Categorize Agent → Classify ticket")
print("  2. Priority Agent → Assign priority")
print("  3. Retrieval Agent → Search KB")
print("  4. Solution Agent → Generate solution")
print("\nPattern: Sequential pipeline with shared state")
print("Framework: LangGraph StateGraph")
print(f"\nView traces: MLflow UI → multi-agent-supervisor → Traces")
