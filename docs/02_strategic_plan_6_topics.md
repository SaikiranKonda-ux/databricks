# Strategic Plan: 6 AI Topics Implementation

## Topic Sequence & Dependencies

```
1. Vector DB (Algorithm) → Already partially done, complete with queries
2. Tracing → Set up early for observability
3. Agent Tools Registry → Required for agents
4. Prompt Registry → Required for agents
5. Multi-Agent & Agent-to-Agent → Uses tools + prompts
6. MCP → Advanced integration using all above
```

---

## Topic 1: Vector DB (HNSW Algorithm)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 1.1 | Understand HNSW algorithm | N/A | [Vector Search Algorithm](https://docs.databricks.com/aws/en/vector-search/vector-search) |
| 1.2 | Query vector index | Catalog → ts_dlh_dev_catalog → assets → kb_vs_index | [Query Vector Search](https://docs.databricks.com/aws/en/vector-search/query-vector-search) |
| 1.3 | Similarity search demo | MLflow Experiments → Runs | [Vector Search Hands-On](https://awadrahman.medium.com/showcasing-databricks-vector-search-a-hands-on-example-2-c231fed0d4fd) |
| 1.4 | Metadata filtering | Catalog → Vector Index → Filter | [Vector Search Retrieval Quality](https://learn.microsoft.com/en-us/azure/databricks/vector-search/vector-search-retrieval-quality) |

### Code Structure
```
notebooks/02_vector_db/
  01_vector_search_basics.py         # Query, similarity search
  02_vector_metadata_filtering.py     # Filtering by category, date
  03_vector_performance_comparison.py # HNSW vs brute force
```

### Key Concepts
- HNSW: Hierarchical Navigable Small World algorithm
- L2 distance metric (Euclidean)
- Endpoint types: Standard (320M vectors) vs Storage-optimized (1B+ vectors)
- Query latency: ~250ms for storage-optimized

---

## Topic 2: Tracing (MLflow Observability)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 2.1 | Enable automatic tracing | MLflow Experiments → Traces tab | [MLflow Tracing Overview](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/) |
| 2.2 | View traces in notebook | Notebook cell output | [Debug with Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/) |
| 2.3 | Timeline/waterfall view | MLflow UI → Experiment → Traces → Trace ID | [View Traces UI](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/ui-traces) |
| 2.4 | Production tracing | Serving Endpoints → Inference Tables → Traces | [Trace Deployed Agents](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/prod-tracing) |

### Code Structure
```
notebooks/03_tracing/
  01_enable_tracing.py                # mlflow.trace() decorator
  02_trace_llm_calls.py               # Trace Azure OpenAI calls
  03_trace_vector_search.py           # Trace retrieval operations
  04_view_traces_ui.py                # Navigate to traces in UI
```

### Key Concepts
- OpenTelemetry-compatible tracing
- Captures: inputs, outputs, prompts, retrievals, tool calls, latency
- Side-by-side comparison in MLflow 3.7+
- Automatic for Mosaic AI Agent Framework

---

## Topic 3: Agent Tools Registry (Unity Catalog Functions)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 3.1 | Create Python UDF | Catalog → ts_dlh_dev_catalog → assets → Functions | [Unity Catalog UDFs](https://docs.databricks.com/aws/en/udf/unity-catalog) |
| 3.2 | Register as UC function | Catalog → Functions → Create | [Create Custom Tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool) |
| 3.3 | Test function in notebook | SQL Editor or Notebook | [UC Functions Reference](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/catalog/functions.html) |
| 3.4 | Grant permissions | Catalog → Function → Permissions | [UC Best Practices](https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices) |

### Code Structure
```
notebooks/06_tools_registry/
  01_create_simple_tool.py            # calculate_priority_score()
  02_create_uc_function_sql.py        # SQL-based function
  03_create_uc_function_python.py     # Python UDF
  04_test_tools.py                    # Test all registered tools
```

### Sample Tools
```python
# ts_dlh_dev_catalog.assets.calculate_priority_score
# ts_dlh_dev_catalog.assets.extract_ticket_entities
# ts_dlh_dev_catalog.assets.route_to_team
```

### Key Concepts
- UC Functions = catalog.schema.function_name
- Requires serverless compute (DBR 15.0+)
- Permissions: EXECUTE, MANAGE
- Can be called by agents as tools

---

## Topic 4: Prompt Registry (MLflow Prompts)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 4.1 | Create prompt via UI | Playground → Prompts or MLflow → Experiment → Prompts | [Create and Edit Prompts](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts) |
| 4.2 | Version prompt | Catalog → Schema → Prompts → Version | [Prompt Registry Overview](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/) |
| 4.3 | Use prompt in code | Notebook | [Use Prompts in Apps](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps) |
| 4.4 | Track lineage | MLflow Experiments → Runs → Artifacts | [Track Prompts with Apps](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions) |

### Code Structure
```
notebooks/05_prompt_registry/
  01_create_prompts.py                # Register prompts in UC
  02_version_prompts.py               # Update and version
  03_use_prompts_in_agents.py         # Load from registry
  04_prompt_lineage.py                # Track usage
```

### Sample Prompts
```
ts_dlh_dev_catalog.assets.classify_ticket_prompt_v1
ts_dlh_dev_catalog.assets.extract_entities_prompt_v1
ts_dlh_dev_catalog.assets.generate_solution_prompt_v1
```

### Key Concepts
- Git-like versioning for prompts
- Non-engineers can modify via UI
- Integration with LangChain, LlamaIndex
- Aliases: production, staging, champion

---

## Topic 5: Multi-Agent & Agent-to-Agent (LangGraph)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 5.1 | Create single agent | MLflow → Agents → Create | [Author AI Agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent) |
| 5.2 | Build LangGraph workflow | Notebook → Graph visualization | [Multi-Agent Tutorial](https://docs.databricks.com/aws/en/generative-ai/tutorials/agent-framework-notebook) |
| 5.3 | Supervisor pattern | Playground → Test multi-agent | [Multi-Agent Supervisor](https://www.databricks.com/blog/multi-agent-supervisor-architecture-orchestrating-enterprise-ai-scale) |
| 5.4 | Deploy multi-agent | Serving → Endpoints → Agent | [Use Genie in Multi-Agent](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-genie) |

### Code Structure
```
notebooks/08_multi_agent/
  01_single_agent_classifier.py      # Ticket classifier
  02_single_agent_router.py          # Ticket router
  03_supervisor_pattern.py           # LangGraph supervisor
  04_agent_to_agent_communication.py # Shared state, Send API
  05_deploy_multi_agent.py           # Register and serve
```

### Communication Patterns
- **Supervisor**: Routes queries to specialized sub-agents
- **Sequential**: Agent 1 → Agent 2 → Agent 3
- **Parallel**: Multiple agents process simultaneously
- **Send API**: Dynamic worker creation

### Key Concepts
- LangGraph: Agent workflows as DAG
- AgentState: Shared data between agents
- Tools: UC functions as agent capabilities
- Tracing: Automatic for all agent calls

---

## Topic 6: MCP (Model Context Protocol)

### Stages

| Stage | Implementation | UI Path | UI Reference |
|-------|---------------|---------|--------------|
| 6.1 | Use managed MCP server | Playground → Add MCP Server → Managed | [Managed MCP Servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp) |
| 6.2 | Create custom MCP server | Databricks Apps → Deploy | [Host MCP on Databricks](https://medium.com/@AI-on-Databricks/building-custom-mcp-servers-on-databricks-apps-a-practical-guide-48048480ce62) |
| 6.3 | Connect MCP to agent | Playground → Agent → Tools | [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/) |
| 6.4 | Test in Playground | Playground → Custom MCP Server | [Connect MCP Tutorial](https://medium.com/@AI-on-Databricks/connect-a-model-context-protocol-mcp-server-with-databricks-cfe22078033d) |

### Code Structure
```
notebooks/11_mcp/
  01_use_managed_mcp.py               # Vector Search MCP server
  02_create_custom_mcp.py             # Custom server for external API
  03_deploy_mcp_as_app.py             # Databricks App deployment
  04_agent_with_mcp.py                # Agent using MCP tools
```

### MCP Types
- **Managed**: Vector Search, Unity Catalog
- **Custom**: External APIs, databases, services
- **Third-party**: Community MCP servers

### Key Concepts
- Open source standard for agent tools
- Databricks Apps host MCP servers (port 8000)
- Unity Catalog permissions enforced
- Test in AI Playground

---

## Implementation Pipeline Order

### Phase 1: Foundation (Already Done)
- ✅ Catalog, schemas, tables, volumes
- ✅ Vector endpoint and index
- ✅ Sample data loaded

### Phase 2: Exploration & Setup
- **02_vector_db/** (30 min)
- **03_tracing/** (20 min)

### Phase 3: Building Blocks
- **06_tools_registry/** (40 min)
- **05_prompt_registry/** (30 min)

### Phase 4: Agents
- **07_single_agent/** (60 min) - Note: Will create this
- **08_multi_agent/** (90 min)

### Phase 5: Advanced
- **11_mcp/** (60 min)

**Total Estimated Time**: ~5.5 hours of hands-on implementation

---

## UI Navigation Quick Reference

### Catalog Explorer
```
Workspace → Catalog → ts_dlh_dev_catalog
├── data (schema)
│   ├── tickets (table)
│   ├── kb_documents (table)
│   └── kb_docs_volume (volume)
└── assets (schema)
    ├── ticket_embeddings (table)
    ├── kb_vs_index (vector index)
    ├── [functions]
    └── [prompts]
```

### MLflow UI
```
Workspace → Machine Learning → Experiments
├── [Your Experiment]
│   ├── Runs tab
│   ├── Traces tab (MLflow Tracing)
│   ├── Prompts tab (Prompt Registry)
│   └── Models tab
```

### AI Tools
```
Workspace → Machine Learning
├── Vector Search → Endpoints → dev_support_ep
├── Serving → Endpoints → [Agent Endpoints]
└── Playground → Test agents, models, MCP

Workspace → Workspace (left sidebar)
├── Your notebooks
└── Databricks Apps (for MCP servers)
```

---

## Documentation URLs by Topic

### Vector DB
- [Vector Search Overview](https://docs.databricks.com/aws/en/vector-search/vector-search)
- [Query Vector Index](https://docs.databricks.com/aws/en/vector-search/query-vector-search)
- [HNSW Algorithm Details](https://community.databricks.com/t5/generative-ai/databricks-vector-search-algorithm/td-p/142623)
- [Hands-On Tutorial](https://awadrahman.medium.com/showcasing-databricks-vector-search-a-hands-on-example-2-c231fed0d4fd)

### Tracing
- [MLflow Tracing Overview](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/)
- [View Traces in UI](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/ui-traces)
- [Debug with Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/)
- [Production Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/prod-tracing)

### Tools Registry
- [Unity Catalog UDFs](https://docs.databricks.com/aws/en/udf/unity-catalog)
- [Create Custom Tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool)
- [Azure: Create Tools](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/create-custom-tool)
- [Functions SDK](https://databricks-sdk-py.readthedocs.io/en/latest/workspace/catalog/functions.html)

### Prompt Registry
- [Prompt Registry Overview](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/)
- [Create and Edit Prompts](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/create-and-edit-prompts)
- [Use Prompts in Apps](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/use-prompts-in-deployed-apps)
- [Track Lineage](https://docs.databricks.com/aws/en/mlflow3/genai/prompt-version-mgmt/prompt-registry/track-prompts-app-versions)

### Multi-Agent
- [Author AI Agents](https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent)
- [Agent Tutorial](https://docs.databricks.com/aws/en/generative-ai/tutorials/agent-framework-notebook)
- [Multi-Agent Supervisor](https://www.databricks.com/blog/multi-agent-supervisor-architecture-orchestrating-enterprise-ai-scale)
- [Multi-Agent Sales Support (2026)](https://medium.com/@AI-on-Databricks/multi-ai-powered-sales-support-databricks-with-langchain-gepa-prompt-optimization-8104654bb538)
- [Use Genie in Multi-Agent](https://docs.databricks.com/aws/en/generative-ai/agent-framework/multi-agent-genie)
- [LangGraph Tutorial](https://langchain-tutorials.github.io/langgraph-multi-agent-systems-2026/)

### MCP
- [MCP on Databricks](https://docs.databricks.com/aws/en/generative-ai/mcp/)
- [Managed MCP Servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp)
- [Host Custom MCP](https://medium.com/@AI-on-Databricks/building-custom-mcp-servers-on-databricks-apps-a-practical-guide-48048480ce62)
- [Connect MCP Tutorial](https://medium.com/@AI-on-Databricks/connect-a-model-context-protocol-mcp-server-with-databricks-cfe22078033d)
- [GitHub: MCP Databricks Server](https://github.com/RafaelCartenet/mcp-databricks-server)

---

## Next Steps

1. **Commit 1**: Create functional notebooks for all 6 topics
2. **Test**: Run all notebooks in sequence
3. **Commit 2**: Add UI reference links as markdown cells in each notebook
4. **Documentation**: Update main README with complete learning path

---

## Success Criteria

Each topic notebook should:
- ✅ Run without errors
- ✅ Demonstrate key concepts
- ✅ Include UI navigation comments
- ✅ Log to MLflow (for tracing)
- ✅ Use actual data from ts_dlh_dev_catalog
- ✅ Reference UI paths in markdown cells
