# Databricks notebook source

from pyspark.sql import functions as F
from datetime import datetime, timedelta
from databricks.vector_search.client import VectorSearchClient
import random
import uuid

CATALOG = "ts_dlh_dev_catalog"
SCHEMA_DATA = "data"
SCHEMA_AI = "assets"
VOLUME_NAME = "kb_docs_volume"
VECTOR_ENDPOINT = "dev_support_ep"
VECTOR_INDEX = "kb_vs_index"

SCHEMA_DATA_FQN = f"{CATALOG}.{SCHEMA_DATA}"
SCHEMA_AI_FQN = f"{CATALOG}.{SCHEMA_AI}"
VOLUME_FQN = f"{CATALOG}.{SCHEMA_DATA}.{VOLUME_NAME}"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.{VECTOR_INDEX}"

# COMMAND ----------

ticket_templates = [
    ("My payment failed", "I tried to make a payment yesterday but it keeps failing. Order #12345. Please help.", "billing", "high"),
    ("Subscription not working", "I paid for premium subscription but still seeing ads. Transaction ID: ABC123", "billing", "medium"),
    ("Refund request", "I want to cancel my subscription and get a refund for this month", "billing", "low"),
    ("Double charged", "I was charged twice for the same order. Please refund one payment immediately.", "billing", "urgent"),
    ("App crashes on startup", "The mobile app crashes every time I try to open it. iPhone 13, iOS 16.", "technical", "high"),
    ("Cannot login", "I'm getting 'invalid credentials' error but my password is correct", "technical", "high"),
    ("Slow performance", "The dashboard is very slow to load, taking 30+ seconds", "technical", "medium"),
    ("Feature not working", "The export to PDF button does nothing when I click it", "technical", "medium"),
    ("Error message", "Getting error code 500 when trying to upload files", "technical", "urgent"),
    ("Password reset not working", "The password reset link in email doesn't work", "account", "high"),
    ("Cannot update profile", "When I try to update my email address, it says 'invalid format'", "account", "low"),
    ("Account locked", "My account got locked after 3 failed login attempts", "account", "high"),
    ("Delete account", "I want to permanently delete my account and all data", "account", "low"),
    ("How to use feature X", "I cannot find where to enable dark mode in settings", "product", "low"),
    ("API documentation", "Where can I find the API documentation for webhooks?", "product", "low"),
    ("Feature request", "Please add two-factor authentication for better security", "product", "low"),
    ("Integration help", "How do I integrate with Salesforce?", "product", "medium"),
]

tickets_data = []
sources = ["email", "chat", "phone", "web"]

for i in range(100):
    template = random.choice(ticket_templates)
    ticket_id = f"TKT-{str(uuid.uuid4())[:8]}"
    customer_id = f"CUST-{random.randint(1000, 9999)}"
    created_ts = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    source = random.choice(sources)

    tickets_data.append({
        "ticket_id": ticket_id,
        "ticket_text": template[1],
        "subject": template[0],
        "customer_id": customer_id,
        "created_timestamp": created_ts,
        "source": source
    })

tickets_df = spark.createDataFrame(tickets_data)
tickets_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_DATA_FQN}.tickets")

print(f"Loaded {tickets_df.count()} tickets")

# COMMAND ----------

kb_documents = [
    {
        "doc_id": "KB-001",
        "doc_name": "Payment Failure Troubleshooting",
        "content": """Common reasons for payment failures: 1. Insufficient funds 2. Incorrect card details 3. Card blocked by bank 4. International transaction blocked. Resolution: Verify card details, check with bank, try alternative payment, contact billing support. Error codes: ERR_PAYMENT_001, ERR_PAYMENT_002""",
        "category": "billing"
    },
    {
        "doc_id": "KB-002",
        "doc_name": "Subscription Management Guide",
        "content": """Subscription management: Upgrade via Settings > Subscription > Upgrade. Downgrade contact support 7 days before renewal. Cancel in Settings (refund within 14 days). Tiers: Free (basic, ads), Premium ($9.99/month, ad-free), Enterprise (custom pricing). Billing monthly. Payment: Credit card, PayPal, bank transfer.""",
        "category": "billing"
    },
    {
        "doc_id": "KB-003",
        "doc_name": "Mobile App Troubleshooting",
        "content": """App crashes: iOS: Force close, restart phone, update from App Store, clear cache in Settings > App, reinstall. Android: Force stop in Settings > Apps, clear cache/data, update Play Store, restart device, reinstall. Minimum: iOS 14+, Android 10+""",
        "category": "technical"
    },
    {
        "doc_id": "KB-004",
        "doc_name": "Login Issues Resolution",
        "content": """Login problems: 1. Verify credentials (check caps lock). 2. Clear browser cache/cookies. 3. Check account status (locked after 5 fails, auto-unlock 30 min). 4. Check 2FA code. Error codes: ERR_AUTH_001 (invalid credentials), ERR_AUTH_002 (locked), ERR_AUTH_003 (session expired)""",
        "category": "technical"
    },
    {
        "doc_id": "KB-005",
        "doc_name": "Performance Optimization Guide",
        "content": """Slow performance fixes: Browser: Clear cache/cookies, disable extensions, try incognito, update browser. Network: Check speed (5 Mbps min), use wired connection, disable VPN. Application: Reduce data range, close tabs, restart browser, try Chrome. Expected: Dashboard <3s, Reports <10s.""",
        "category": "technical"
    },
    {
        "doc_id": "KB-006",
        "doc_name": "Password Reset Procedure",
        "content": """Password reset: Click Forgot Password, enter email, check inbox/spam, click link within 1 hour, create new password (8+ chars, uppercase, number, special char). Link issues: expires 1 hour, request new, copy-paste link, try different browser. No email: check spam, verify email address, add noreply@company.com to contacts, contact support after 10 min.""",
        "category": "account"
    },
    {
        "doc_id": "KB-007",
        "doc_name": "Account Security Best Practices",
        "content": """Security: Strong password (12+ chars, mixed case, numbers, symbols), use password manager. Enable 2FA in Settings > Security. Monthly security checks: review login history, check devices, revoke unused. Recognize phishing: verify sender, hover links, report to security@company.com. If compromised: change password, enable 2FA, review activity, contact support.""",
        "category": "account"
    },
    {
        "doc_id": "KB-008",
        "doc_name": "Data Export and Backup",
        "content": """Export data: Settings > Data Management > Export, select data types, choose format (CSV/JSON/Excel), request export, download link via email (48h availability). Includes: profile, content, settings, logs. Max 5GB, larger split into files. Processing: 5min-2h. Enterprise: automatic daily backups, 30-day retention. GDPR compliant.""",
        "category": "product"
    },
    {
        "doc_id": "KB-009",
        "doc_name": "API Integration Guide",
        "content": """API setup: Generate key in Settings > Developers > API Keys (90-day expiry). Auth: Bearer token. Rate limit: 1000/hr (Free), 10000/hr (Premium). Endpoints: GET /api/v1/user, POST /api/v1/data, PUT /api/v1/data/:id, DELETE /api/v1/data/:id. Webhooks in Settings > Developers. Docs: https://api.company.com/docs. SDKs: Python, JavaScript, Java, PHP.""",
        "category": "product"
    },
    {
        "doc_id": "KB-010",
        "doc_name": "Error Code Reference",
        "content": """Error codes: Auth: ERR_AUTH_001 (invalid credentials), ERR_AUTH_002 (locked), ERR_AUTH_003 (session expired), ERR_AUTH_004 (2FA invalid). Payment: ERR_PAYMENT_001 (card declined), ERR_PAYMENT_002 (insufficient funds), ERR_PAYMENT_003 (gateway timeout). Technical: ERR_500 (internal error), ERR_503 (unavailable), ERR_UPLOAD_001 (file too large, 100MB max), ERR_UPLOAD_002 (invalid type). Network: ERR_NETWORK_001 (timeout), ERR_NETWORK_002 (DNS failed).""",
        "category": "technical"
    },
    {
        "doc_id": "KB-011",
        "doc_name": "Contact Support Channels",
        "content": """Support: Live chat (24/7 Premium, Mon-Fri 9-5 EST Free, 2min response). Email support@company.com (24h Premium, 48h Free). Phone +1-800-123-4567 (Premium only, Mon-Fri 9-9 EST, 5min wait). Help Center: help.company.com. Twitter @CompanySupport (1-2h response). Priority: Urgent (system down), High (cannot login), Medium (performance), Low (feature requests).""",
        "category": "product"
    },
    {
        "doc_id": "KB-012",
        "doc_name": "Account Deletion and Data Privacy",
        "content": """Delete account: Settings > Account > Delete Account, verify password, confirm via email, deleted within 24h. Data: Personal deleted 30 days, content immediate, backups purged 90 days, analytics anonymized. Alternatives: deactivate account, export data first. GDPR rights: access, rectification, erasure, portability, object to processing. Recovery: 30-day grace period. Privacy: privacy.company.com. DPO: dpo@company.com.""",
        "category": "account"
    }
]

kb_df = spark.createDataFrame(kb_documents).withColumn("created_timestamp", F.current_timestamp())
kb_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_DATA_FQN}.kb_documents")

print(f"Loaded {kb_df.count()} KB documents")

# COMMAND ----------

embeddings_df = spark.sql(f"""
    SELECT
        doc_id as ticket_id,
        CONCAT(doc_name, ': ', content) as content,
        current_timestamp() as created_timestamp
    FROM {SCHEMA_DATA_FQN}.kb_documents
""")

embeddings_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_AI_FQN}.ticket_embeddings")

print(f"Created embeddings table: {embeddings_df.count()} records")

# COMMAND ----------

volume_path = f"/Volumes/{CATALOG}/{SCHEMA_DATA}/{VOLUME_NAME}"

dbutils.fs.put(f"{volume_path}/troubleshooting_guide.txt", """IT TROUBLESHOOTING QUICK REFERENCE
1. NETWORK: Check cables, WiFi enabled, restart router, ipconfig release/renew, check firewall
2. PERFORMANCE: Check CPU usage, close apps, disk cleanup, malware scan, check disk space
3. PRINTER: Power on, set default, clear queue, update drivers, check ink
4. EMAIL: Check connection, verify settings, clear cache, increase storage, check spam
5. SOFTWARE CRASHES: Update version, clear cache, reinstall, check requirements, review logs
Help Desk: ext 5000""", overwrite=True)

dbutils.fs.put(f"{volume_path}/security_best_practices.txt", """INFORMATION SECURITY BEST PRACTICES
PASSWORD: 12+ chars, password manager, enable MFA, never share, change if compromised
PHISHING: Verify sender, don't click suspicious links, hover to see URL, report to security@company.com
DATA: Encrypt sensitive data, use VPN on public WiFi, lock screen, shred documents
DEVICE: Update OS/software, antivirus, firewall, encrypt drive, remote wipe, report lost/stolen
INCIDENT: Disconnect if infected, contact IT Security, document, preserve evidence
Security Hotline: +1-800-SEC-RITY""", overwrite=True)

dbutils.fs.put(f"{volume_path}/onboarding_checklist.txt", """NEW EMPLOYEE IT ONBOARDING
DAY 1: Laptop, email, MFA, software, intranet, security training, phone, Slack
WEEK 1: VPN, system access, cybersecurity training, printer, backup, IT policies, calendar
MONTH 1: Software training, integrations, verify permissions, IT 1:1, data classification, incident procedures, mobile device, privacy training
CONTACTS: helpdesk@company.com / ext 5000
Welcome!""", overwrite=True)

print(f"Uploaded files to {volume_path}")

# COMMAND ----------

client = VectorSearchClient()

endpoint_info = client.get_endpoint(name=VECTOR_ENDPOINT)
endpoint_state = endpoint_info.get('endpoint_status', {}).get('state', 'Unknown')

print(f"Endpoint: {VECTOR_ENDPOINT}, Status: {endpoint_state}")

if endpoint_state == "ONLINE":
    try:
        try:
            existing_index = client.get_index(name=VECTOR_INDEX_FQN)
            client.delete_index(name=VECTOR_INDEX_FQN)
        except:
            pass

        index = client.create_delta_sync_index(
            endpoint_name=VECTOR_ENDPOINT,
            index_name=VECTOR_INDEX_FQN,
            source_table_name=f"{SCHEMA_AI_FQN}.ticket_embeddings",
            pipeline_type="TRIGGERED",
            primary_key="ticket_id",
            embedding_source_column="content",
            embedding_model_endpoint_name="databricks-bge-large-en"
        )

        print(f"Vector index created: {VECTOR_INDEX_FQN}")
    except Exception as e:
        print(f"Error: {str(e)}")
else:
    print(f"Endpoint not ready: {endpoint_state}")

# COMMAND ----------

print(f"Data loaded: 100 tickets, 12 KB docs, 12 embeddings, 3 files")
print(f"Vector index: {VECTOR_INDEX_FQN}")
