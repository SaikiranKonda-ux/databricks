# Databricks notebook source
# MAGIC %md
# MAGIC # Topic 6: Model Context Protocol (MCP) - Enterprise Tool Integration
# MAGIC
# MAGIC **UI Path**: Workspace → Playground → Add MCP Server (button) → Managed or Custom
# MAGIC
# MAGIC **Test MCP**: AI Playground → Tools → Select MCP servers
# MAGIC
# MAGIC **Documentation**:
# MAGIC - [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/)
# MAGIC - [Managed MCP Servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp)
# MAGIC - [Host Custom MCP](https://medium.com/@AI-on-Databricks/building-custom-mcp-servers-on-databricks-apps-a-practical-guide-48048480ce62)
# MAGIC - [GitHub: MCP Server Example](https://github.com/RafaelCartenet/mcp-databricks-server)

# COMMAND ----------

import os
from databricks_mcp import DatabricksMCPClient

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.kb_vs_index"

# COMMAND ----------

mcp_client = DatabricksMCPClient()

available_servers = mcp_client.list_servers()
print("Available Managed MCP Servers:")
for server in available_servers:
    print(f"  - {server['name']}: {server['type']}")

# COMMAND ----------

vector_search_mcp = {
    "type": "vector_search",
    "config": {
        "index_name": VECTOR_INDEX_FQN,
        "columns": ["ticket_id", "content"],
        "num_results": 5
    }
}

mcp_client.add_server("kb_vector_search", vector_search_mcp)
print(f"Added MCP server: kb_vector_search for {VECTOR_INDEX_FQN}")

# COMMAND ----------

uc_functions_mcp = {
    "type": "unity_catalog_functions",
    "config": {
        "catalog": CATALOG,
        "schema": SCHEMA_AI,
        "functions": [
            "calculate_priority_score",
            "extract_category",
            "route_to_team"
        ]
    }
}

mcp_client.add_server("uc_tools", uc_functions_mcp)
print(f"Added MCP server: uc_tools for UC functions")

# COMMAND ----------

from openai import AzureOpenAI

AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

tools = mcp_client.get_tools()

messages = [
    {"role": "system", "content": "You are a support ticket assistant with access to KB search and classification tools."},
    {"role": "user", "content": "Search for payment failure solutions and classify priority"}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

print("Agent Response with MCP Tools:")
print(response.choices[0].message.content)

if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"\nTool Called: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")

# COMMAND ----------

print("\nMCP (Model Context Protocol) Setup Complete:")
print("  - Managed MCP Server: Vector Search")
print("  - Managed MCP Server: Unity Catalog Functions")
print("  - Integration: Azure OpenAI with MCP tools")
print("\nBenefits:")
print("  - Standardized tool interface")
print("  - Automatic Unity Catalog permissions")
print("  - Multi-source data access")
print("  - Scalable tool management")
print("\nWithout MCP: Manual tool integration, no standard protocol")
print("With MCP: Plug-and-play tools, centralized management")
