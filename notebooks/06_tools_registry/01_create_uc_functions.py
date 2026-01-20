# Databricks notebook source
# MAGIC %md
# MAGIC # Topic 3: Agent Tools Registry - Unity Catalog Functions
# MAGIC
# MAGIC **UI Path**: Catalog → ts_dlh_dev_catalog → assets → Functions
# MAGIC
# MAGIC **View Functions**: Click on function name to see definition, permissions, lineage
# MAGIC
# MAGIC **Documentation**:
# MAGIC - [Unity Catalog UDFs](https://docs.databricks.com/aws/en/udf/unity-catalog)
# MAGIC - [Create Custom Tools](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool)
# MAGIC - [Azure: Create Tools](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-framework/create-custom-tool)

# COMMAND ----------

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_AI = "assets"
SCHEMA_AI_FQN = f"{CATALOG}.{SCHEMA_AI}"

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {SCHEMA_AI_FQN}.calculate_priority_score(
    keywords STRING
)
RETURNS INT
LANGUAGE SQL
COMMENT 'Calculate priority score based on keywords in ticket text'
RETURN CASE
    WHEN keywords LIKE '%urgent%' OR keywords LIKE '%critical%' OR keywords LIKE '%down%' THEN 4
    WHEN keywords LIKE '%high%' OR keywords LIKE '%cannot%' OR keywords LIKE '%error%' THEN 3
    WHEN keywords LIKE '%medium%' OR keywords LIKE '%slow%' OR keywords LIKE '%issue%' THEN 2
    ELSE 1
END
""")

print(f"Created: {SCHEMA_AI_FQN}.calculate_priority_score")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {SCHEMA_AI_FQN}.extract_category(
    ticket_text STRING
)
RETURNS STRING
LANGUAGE SQL
COMMENT 'Extract category from ticket text based on keywords'
RETURN CASE
    WHEN ticket_text LIKE '%payment%' OR ticket_text LIKE '%billing%' OR ticket_text LIKE '%refund%' THEN 'billing'
    WHEN ticket_text LIKE '%login%' OR ticket_text LIKE '%password%' OR ticket_text LIKE '%account%' THEN 'account'
    WHEN ticket_text LIKE '%crash%' OR ticket_text LIKE '%error%' OR ticket_text LIKE '%bug%' THEN 'technical'
    WHEN ticket_text LIKE '%how to%' OR ticket_text LIKE '%API%' OR ticket_text LIKE '%feature%' THEN 'product'
    ELSE 'general'
END
""")

print(f"Created: {SCHEMA_AI_FQN}.extract_category")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {SCHEMA_AI_FQN}.route_to_team(
    category STRING,
    priority INT
)
RETURNS STRING
LANGUAGE SQL
COMMENT 'Route ticket to appropriate team based on category and priority'
RETURN CASE
    WHEN category = 'billing' THEN 'finance_team'
    WHEN category = 'account' THEN 'support_team'
    WHEN category = 'technical' AND priority >= 3 THEN 'engineering_team'
    WHEN category = 'technical' AND priority < 3 THEN 'support_l2_team'
    WHEN category = 'product' THEN 'product_team'
    ELSE 'support_l1_team'
END
""")

print(f"Created: {SCHEMA_AI_FQN}.route_to_team")

# COMMAND ----------

spark.sql(f"SHOW FUNCTIONS IN {SCHEMA_AI_FQN}").filter("function LIKE '%calculate%' OR function LIKE '%extract%' OR function LIKE '%route%'").show(truncate=False)

# COMMAND ----------

test_df = spark.sql(f"""
SELECT
    'Payment failed' as ticket_text,
    {SCHEMA_AI_FQN}.calculate_priority_score('Payment failed urgent') as priority,
    {SCHEMA_AI_FQN}.extract_category('Payment failed urgent') as category
""")

test_df = test_df.withColumn(
    "team",
    spark.sql(f"SELECT {SCHEMA_AI_FQN}.route_to_team(category, priority) as team FROM test_df").collect()[0][0]
)

test_df.show(truncate=False)

print("\nUC Functions created as agent tools:")
print(f"  - {SCHEMA_AI_FQN}.calculate_priority_score()")
print(f"  - {SCHEMA_AI_FQN}.extract_category()")
print(f"  - {SCHEMA_AI_FQN}.route_to_team()")
