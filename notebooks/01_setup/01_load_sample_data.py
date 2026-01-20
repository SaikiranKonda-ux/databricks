# Databricks notebook source
# MAGIC %md
# MAGIC # Load Sample Data - Customer Support Tickets & Knowledge Base
# MAGIC
# MAGIC **Purpose**: Load sample data for AI Applications learning
# MAGIC
# MAGIC **What this notebook does**:
# MAGIC 1. Generate sample support tickets
# MAGIC 2. Create knowledge base documents
# MAGIC 3. Load data into Delta tables
# MAGIC 4. Upload documents to Unity Catalog volume
# MAGIC 5. Create vector search index

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

# Import libraries
from pyspark.sql import functions as F
from datetime import datetime, timedelta
import random
import uuid

# Configuration (match your catalog/schema names)
CATALOG = "ts_dlh_dev_catalog"
SCHEMA_DATA = "data"
SCHEMA_AI = "assets"
VOLUME_NAME = "kb_docs_volume"
VECTOR_ENDPOINT = "dev_support_ep"
VECTOR_INDEX = "kb_vs_index"

# Full qualified names
SCHEMA_DATA_FQN = f"{CATALOG}.{SCHEMA_DATA}"
SCHEMA_AI_FQN = f"{CATALOG}.{SCHEMA_AI}"
VOLUME_FQN = f"{CATALOG}.{SCHEMA_DATA}.{VOLUME_NAME}"
VECTOR_INDEX_FQN = f"{CATALOG}.{SCHEMA_AI}.{VECTOR_INDEX}"

print(f"✅ Configuration loaded")
print(f"   Catalog: {CATALOG}")
print(f"   Data Schema: {SCHEMA_DATA_FQN}")
print(f"   AI Schema: {SCHEMA_AI_FQN}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Generate Sample Support Tickets
# MAGIC
# MAGIC Creating 100 realistic support tickets across different categories

# COMMAND ----------

# Sample ticket templates
ticket_templates = [
    # Billing Issues
    ("My payment failed", "I tried to make a payment yesterday but it keeps failing. Order #12345. Please help.", "billing", "high"),
    ("Subscription not working", "I paid for premium subscription but still seeing ads. Transaction ID: ABC123", "billing", "medium"),
    ("Refund request", "I want to cancel my subscription and get a refund for this month", "billing", "low"),
    ("Double charged", "I was charged twice for the same order. Please refund one payment immediately.", "billing", "urgent"),

    # Technical Issues
    ("App crashes on startup", "The mobile app crashes every time I try to open it. iPhone 13, iOS 16.", "technical", "high"),
    ("Cannot login", "I'm getting 'invalid credentials' error but my password is correct", "technical", "high"),
    ("Slow performance", "The dashboard is very slow to load, taking 30+ seconds", "technical", "medium"),
    ("Feature not working", "The export to PDF button does nothing when I click it", "technical", "medium"),
    ("Error message", "Getting error code 500 when trying to upload files", "technical", "urgent"),

    # Account Issues
    ("Password reset not working", "The password reset link in email doesn't work", "account", "high"),
    ("Cannot update profile", "When I try to update my email address, it says 'invalid format'", "account", "low"),
    ("Account locked", "My account got locked after 3 failed login attempts", "account", "high"),
    ("Delete account", "I want to permanently delete my account and all data", "account", "low"),

    # Product Questions
    ("How to use feature X", "I cannot find where to enable dark mode in settings", "product", "low"),
    ("API documentation", "Where can I find the API documentation for webhooks?", "product", "low"),
    ("Feature request", "Please add two-factor authentication for better security", "product", "low"),
    ("Integration help", "How do I integrate with Salesforce?", "product", "medium"),
]

# Generate 100 tickets
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
        "ticket_text": template[1],  # description
        "subject": template[0],       # subject
        "customer_id": customer_id,
        "created_timestamp": created_ts,
        "source": source
    })

# Create DataFrame
tickets_df = spark.createDataFrame(tickets_data)

# Show sample
print(f"✅ Generated {tickets_df.count()} sample tickets")
tickets_df.show(5, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Load Tickets into Delta Table

# COMMAND ----------

# Write to Delta table
tickets_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_DATA_FQN}.tickets")

print(f"✅ Loaded {tickets_df.count()} tickets into {SCHEMA_DATA_FQN}.tickets")

# Verify
ticket_count = spark.table(f"{SCHEMA_DATA_FQN}.tickets").count()
print(f"   Verified: {ticket_count} rows in table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Knowledge Base Documents
# MAGIC
# MAGIC Creating 12 knowledge base documents covering common IT support topics

# COMMAND ----------

kb_documents = [
    {
        "doc_id": "KB-001",
        "doc_name": "Payment Failure Troubleshooting",
        "content": """
        Common reasons for payment failures:
        1. Insufficient funds in the account
        2. Incorrect card details (CVV, expiry date)
        3. Card blocked by issuing bank
        4. International transaction blocked

        Resolution steps:
        - Verify card details are correct
        - Check with bank if card is active for online transactions
        - Try alternative payment method
        - Contact billing support if issue persists

        Related error codes: ERR_PAYMENT_001, ERR_PAYMENT_002
        """,
        "category": "billing"
    },
    {
        "doc_id": "KB-002",
        "doc_name": "Subscription Management Guide",
        "content": """
        How to manage your subscription:

        Upgrade: Go to Settings > Subscription > Upgrade Plan
        Downgrade: Contact support 7 days before renewal
        Cancel: Settings > Subscription > Cancel (refund within 14 days)

        Subscription tiers:
        - Free: Basic features, ads supported
        - Premium: $9.99/month, ad-free, priority support
        - Enterprise: Custom pricing, dedicated account manager

        Billing cycle: Monthly on subscription date
        Payment methods: Credit card, PayPal, bank transfer
        """,
        "category": "billing"
    },
    {
        "doc_id": "KB-003",
        "doc_name": "Mobile App Troubleshooting",
        "content": """
        If the mobile app crashes or doesn't start:

        iOS:
        1. Force close app (swipe up from app switcher)
        2. Restart iPhone
        3. Update app from App Store
        4. Clear app cache: Settings > App > Clear Cache
        5. Reinstall app if needed

        Android:
        1. Force stop: Settings > Apps > [App Name] > Force Stop
        2. Clear cache and data
        3. Update from Play Store
        4. Restart device
        5. Reinstall if issue persists

        Minimum requirements: iOS 14+, Android 10+
        """,
        "category": "technical"
    },
    {
        "doc_id": "KB-004",
        "doc_name": "Login Issues Resolution",
        "content": """
        Cannot login? Try these steps:

        1. Verify credentials
           - Username/email is correct
           - Check caps lock is off
           - Try password reset if unsure

        2. Clear browser cache/cookies
           - Chrome: Settings > Privacy > Clear browsing data
           - Firefox: Settings > Privacy > Clear Data

        3. Check account status
           - Account may be locked after 5 failed attempts
           - Unlock automatically after 30 minutes
           - Or contact support for immediate unlock

        4. Two-factor authentication
           - If enabled, check authenticator app
           - Backup codes available in account settings

        Common error codes:
        - ERR_AUTH_001: Invalid credentials
        - ERR_AUTH_002: Account locked
        - ERR_AUTH_003: Session expired
        """,
        "category": "technical"
    },
    {
        "doc_id": "KB-005",
        "doc_name": "Performance Optimization Guide",
        "content": """
        If the application is slow:

        Browser-related:
        - Clear cache and cookies
        - Disable browser extensions
        - Try incognito/private mode
        - Update browser to latest version

        Network-related:
        - Check internet speed (minimum 5 Mbps recommended)
        - Use wired connection if on WiFi
        - Disable VPN temporarily
        - Try different network

        Application-related:
        - Reduce data range in reports (last 30 days instead of all time)
        - Close unused tabs
        - Restart browser
        - Try different browser (Chrome recommended)

        Expected performance:
        - Dashboard load: < 3 seconds
        - Report generation: < 10 seconds
        - File upload: Depends on size and network
        """,
        "category": "technical"
    },
    {
        "doc_id": "KB-006",
        "doc_name": "Password Reset Procedure",
        "content": """
        To reset your password:

        1. Click 'Forgot Password' on login page
        2. Enter registered email address
        3. Check email inbox (and spam folder)
        4. Click reset link within 1 hour
        5. Create new password (min 8 characters, include uppercase, number, special char)

        If reset link doesn't work:
        - Link expires after 1 hour
        - Request new reset link
        - Copy-paste link instead of clicking
        - Try different browser

        If not receiving email:
        - Check spam/junk folder
        - Verify email address is correct
        - Add noreply@company.com to contacts
        - Contact support if still not received after 10 minutes

        Security tips:
        - Use unique password (not reused from other sites)
        - Enable two-factor authentication
        - Update password every 90 days
        """,
        "category": "account"
    },
    {
        "doc_id": "KB-007",
        "doc_name": "Account Security Best Practices",
        "content": """
        Protect your account:

        1. Strong Password
           - Minimum 12 characters
           - Mix of uppercase, lowercase, numbers, symbols
           - No dictionary words or personal info
           - Use password manager

        2. Two-Factor Authentication (2FA)
           - Enable in Settings > Security
           - Use authenticator app (Google Authenticator, Authy)
           - Save backup codes in safe place

        3. Regular Security Checks
           - Review login history monthly
           - Check connected devices
           - Revoke access for unused devices
           - Update recovery email/phone

        4. Recognize Phishing
           - We never ask for password via email
           - Check sender email domain carefully
           - Hover over links before clicking
           - Report suspicious emails to security@company.com

        5. What to do if compromised:
           - Change password immediately
           - Enable 2FA if not already
           - Review recent account activity
           - Contact support immediately
        """,
        "category": "account"
    },
    {
        "doc_id": "KB-008",
        "doc_name": "Data Export and Backup",
        "content": """
        How to export your data:

        1. Go to Settings > Data Management > Export
        2. Select data types to export (choose all for complete backup)
        3. Choose format: CSV, JSON, or Excel
        4. Click 'Request Export'
        5. Download link sent via email (available 48 hours)

        What's included:
        - User profile information
        - All created content
        - Settings and preferences
        - Activity logs

        Limitations:
        - Maximum export size: 5 GB
        - Larger exports split into multiple files
        - Processing time: 5 minutes to 2 hours depending on data size

        Automated backups:
        - Enterprise plan includes automatic daily backups
        - Retention: 30 days
        - Point-in-time restore available

        GDPR compliance:
        - Right to data portability
        - Export available in machine-readable format
        - Complete within 30 days of request
        """,
        "category": "product"
    },
    {
        "doc_id": "KB-009",
        "doc_name": "API Integration Guide",
        "content": """
        Getting started with our API:

        1. Generate API Key
           - Go to Settings > Developers > API Keys
           - Click 'Create New Key'
           - Save key securely (shown only once)
           - Set expiration period (recommended: 90 days)

        2. Authentication
           - Use Bearer token in header
           - Example: Authorization: Bearer YOUR_API_KEY
           - Rate limit: 1000 requests/hour (Free), 10000/hour (Premium)

        3. Available Endpoints
           - GET /api/v1/user - Get user profile
           - POST /api/v1/data - Create new record
           - PUT /api/v1/data/:id - Update record
           - DELETE /api/v1/data/:id - Delete record

        4. Webhooks
           - Configure in Settings > Developers > Webhooks
           - Supported events: created, updated, deleted
           - Retry policy: 3 attempts with exponential backoff

        5. Documentation
           - Full API docs: https://api.company.com/docs
           - Postman collection available
           - SDKs: Python, JavaScript, Java, PHP

        Support:
        - API support: api-support@company.com
        - Status page: status.company.com
        - Changelog: docs.company.com/changelog
        """,
        "category": "product"
    },
    {
        "doc_id": "KB-010",
        "doc_name": "Error Code Reference",
        "content": """
        Common error codes and resolutions:

        Authentication Errors:
        - ERR_AUTH_001: Invalid credentials - Check username/password
        - ERR_AUTH_002: Account locked - Wait 30 min or contact support
        - ERR_AUTH_003: Session expired - Log in again
        - ERR_AUTH_004: 2FA code invalid - Request new code

        Payment Errors:
        - ERR_PAYMENT_001: Card declined - Contact bank
        - ERR_PAYMENT_002: Insufficient funds - Add funds or use different card
        - ERR_PAYMENT_003: Payment gateway timeout - Retry after 5 minutes

        Technical Errors:
        - ERR_500: Internal server error - Retry or contact support
        - ERR_503: Service unavailable - Check status page
        - ERR_UPLOAD_001: File too large - Max size 100 MB
        - ERR_UPLOAD_002: Invalid file type - Allowed: PDF, JPG, PNG, DOCX

        Network Errors:
        - ERR_NETWORK_001: Connection timeout - Check internet
        - ERR_NETWORK_002: DNS resolution failed - Check network settings

        If error persists:
        1. Note error code
        2. Take screenshot
        3. Contact support with details
        4. Include: time of error, what you were doing, browser/device info
        """,
        "category": "technical"
    },
    {
        "doc_id": "KB-011",
        "doc_name": "Contact Support Channels",
        "content": """
        How to reach our support team:

        1. Live Chat (Fastest)
           - Available in app (bottom right corner)
           - Hours: 24/7 for Premium, Mon-Fri 9am-5pm EST for Free
           - Average response: 2 minutes
           - Best for: Urgent issues, quick questions

        2. Email Support
           - Address: support@company.com
           - Response time: 24 hours (Premium), 48 hours (Free)
           - Best for: Detailed issues, attachments needed
           - Include: Account email, issue description, screenshots

        3. Phone Support (Premium only)
           - Number: +1-800-123-4567
           - Hours: Mon-Fri 9am-9pm EST
           - Average wait: 5 minutes
           - Best for: Complex issues, immediate assistance

        4. Help Center
           - URL: help.company.com
           - Searchable knowledge base
           - Video tutorials
           - Community forums

        5. Social Media
           - Twitter: @CompanySupport (public issues only)
           - Response time: 1-2 hours during business hours

        Priority Levels:
        - Urgent: System down, payment issues
        - High: Cannot login, feature broken
        - Medium: Performance issues, questions
        - Low: Feature requests, general inquiries

        Before contacting:
        - Check Help Center for instant answers
        - Have account information ready
        - Note exact error messages
        - Try basic troubleshooting steps
        """,
        "category": "product"
    },
    {
        "doc_id": "KB-012",
        "doc_name": "Account Deletion and Data Privacy",
        "content": """
        To permanently delete your account:

        Warning: This action is irreversible
        - All data will be permanently deleted
        - Active subscriptions will be cancelled
        - No refunds for partial billing periods
        - Cannot recover account after deletion

        Deletion Process:
        1. Go to Settings > Account > Delete Account
        2. Verify identity (enter password)
        3. Confirm via email link
        4. Account deleted within 24 hours
        5. Confirmation email sent once complete

        What happens to your data:
        - Personal info: Deleted within 30 days
        - Content: Deleted immediately
        - Backups: Purged within 90 days (legal requirement)
        - Analytics: Anonymized and retained (GDPR compliant)

        Alternatives to deletion:
        - Deactivate account (keeps data, stops billing)
        - Download data export first
        - Cancel subscription but keep account

        GDPR Rights:
        - Right to access data
        - Right to rectification
        - Right to erasure (right to be forgotten)
        - Right to data portability
        - Right to object to processing

        Privacy Policy: privacy.company.com
        Data Protection Officer: dpo@company.com

        Recovery period:
        - 30-day grace period for accidental deletions
        - Contact support within 30 days to restore
        - After 30 days, deletion is permanent
        """,
        "category": "account"
    }
]

# Create DataFrame
kb_df = spark.createDataFrame(kb_documents).withColumn("created_timestamp", F.current_timestamp())

print(f"✅ Created {kb_df.count()} knowledge base documents")
kb_df.select("doc_id", "doc_name", "category").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Load Knowledge Base into Delta Table

# COMMAND ----------

# Write to Delta table
kb_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_DATA_FQN}.kb_documents")

print(f"✅ Loaded {kb_df.count()} documents into {SCHEMA_DATA_FQN}.kb_documents")

# Verify
kb_count = spark.table(f"{SCHEMA_DATA_FQN}.kb_documents").count()
print(f"   Verified: {kb_count} rows in table")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Prepare Data for Vector Search
# MAGIC
# MAGIC Combine tickets with KB for embeddings table

# COMMAND ----------

# For this learning exercise, we'll create embeddings from KB documents
# In production, you might also embed historical tickets with resolutions

embeddings_df = spark.sql(f"""
    SELECT
        doc_id as ticket_id,
        CONCAT(doc_name, ': ', content) as content,
        current_timestamp() as created_timestamp
    FROM {SCHEMA_DATA_FQN}.kb_documents
""")

# Write to embeddings table
embeddings_df.write.format("delta").mode("overwrite").saveAsTable(f"{SCHEMA_AI_FQN}.ticket_embeddings")

print(f"✅ Created embeddings table with {embeddings_df.count()} records")
print(f"   Table: {SCHEMA_AI_FQN}.ticket_embeddings")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Upload Sample Files to Volume (Optional)
# MAGIC
# MAGIC For ai_parse_document learning, you can manually upload PDFs to:
# MAGIC `/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/`
# MAGIC
# MAGIC **How to upload**:
# MAGIC 1. Go to Databricks UI > Data > Volumes
# MAGIC 2. Navigate to: ts_dlh_dev_catalog > data > kb_docs_volume
# MAGIC 3. Click "Upload Files"
# MAGIC 4. Drag and drop PDF/DOCX files
# MAGIC
# MAGIC **Sample files to create** (save as .txt first, then upload):
# MAGIC - troubleshooting_guide.txt
# MAGIC - api_documentation.txt
# MAGIC - security_policy.txt

# COMMAND ----------

# Create sample text files programmatically in the volume
volume_path = f"/Volumes/{CATALOG}/{SCHEMA_DATA}/{VOLUME_NAME}"

# Sample file 1
dbutils.fs.put(f"{volume_path}/troubleshooting_guide.txt", """
IT TROUBLESHOOTING QUICK REFERENCE GUIDE

1. NETWORK CONNECTIVITY ISSUES
- Check physical cable connections
- Verify WiFi is enabled
- Restart router/modem (30 second power cycle)
- Run ipconfig /release and ipconfig /renew (Windows)
- Check firewall settings
- Contact ISP if issue persists

2. SLOW COMPUTER PERFORMANCE
- Check CPU usage in Task Manager
- Close unnecessary applications
- Run disk cleanup
- Scan for malware
- Check available disk space (need 15% free minimum)
- Consider RAM upgrade if consistently high memory usage

3. PRINTER NOT WORKING
- Check printer is powered on and connected
- Verify printer is set as default
- Clear print queue
- Update printer drivers
- Run Windows printer troubleshooter
- Check ink/toner levels

4. EMAIL ISSUES
- Verify internet connection
- Check email server settings
- Clear email cache
- Increase mailbox storage
- Check spam/junk folders
- Verify account credentials

5. SOFTWARE CRASHES
- Update to latest version
- Clear application cache
- Reinstall application
- Check system requirements
- Review error logs
- Disable conflicting plugins

For urgent issues, contact IT Help Desk: ext 5000
""", overwrite=True)

# Sample file 2
dbutils.fs.put(f"{volume_path}/security_best_practices.txt", """
INFORMATION SECURITY BEST PRACTICES

PASSWORD MANAGEMENT
- Minimum 12 characters
- Use password manager
- Enable MFA/2FA on all accounts
- Never share passwords
- Change password immediately if compromised
- Use unique passwords for each service

PHISHING AWARENESS
- Verify sender email address carefully
- Don't click suspicious links
- Hover over links to see actual URL
- Be cautious of urgent/threatening messages
- Verify requests through official channels
- Report phishing to security@company.com

DATA PROTECTION
- Encrypt sensitive data
- Use VPN on public WiFi
- Lock screen when away from desk
- Don't leave confidential documents visible
- Shred sensitive paper documents
- Classify data according to company policy

DEVICE SECURITY
- Keep OS and software updated
- Install antivirus software
- Enable firewall
- Encrypt hard drive (BitLocker/FileVault)
- Remote wipe capability for mobile devices
- Report lost/stolen devices immediately

INCIDENT RESPONSE
- Disconnect from network if infected
- Contact IT Security immediately
- Document what happened
- Don't pay ransomware demands
- Preserve evidence for investigation
- Follow incident response procedures

Security Hotline: +1-800-SEC-RITY
Email: security@company.com
""", overwrite=True)

# Sample file 3
dbutils.fs.put(f"{volume_path}/onboarding_checklist.txt", """
NEW EMPLOYEE IT ONBOARDING CHECKLIST

DAY 1
[ ] Receive company laptop
[ ] Set up email account
[ ] Configure MFA/2FA
[ ] Install required software
[ ] Access company intranet
[ ] Complete security training
[ ] Set up desk phone
[ ] Join team Slack channels

FIRST WEEK
[ ] Set up VPN access
[ ] Request access to required systems
[ ] Complete cybersecurity awareness training
[ ] Set up printer access
[ ] Configure backup solution
[ ] Review company IT policies
[ ] Set up calendar and scheduling
[ ] Join department meetings

FIRST MONTH
[ ] Complete role-specific software training
[ ] Set up integrations (Salesforce, JIRA, etc)
[ ] Verify all permissions are correct
[ ] Schedule 1:1 with IT for questions
[ ] Review data classification policy
[ ] Understand incident reporting procedures
[ ] Set up mobile device management
[ ] Complete privacy training

CONTACTS
IT Help Desk: helpdesk@company.com / ext 5000
Manager: [To be assigned]
IT Buddy: [To be assigned]
HR Contact: hr@company.com

Welcome to the team!
""", overwrite=True)

print(f"✅ Uploaded 3 sample text files to volume")
print(f"   Volume path: {volume_path}")
print("\n📄 Files created:")
print("   - troubleshooting_guide.txt")
print("   - security_best_practices.txt")
print("   - onboarding_checklist.txt")

# List files to verify
files = dbutils.fs.ls(volume_path)
print(f"\n📁 Total files in volume: {len(files)}")
for file in files:
    print(f"   - {file.name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Create Vector Search Index
# MAGIC
# MAGIC **Prerequisites**:
# MAGIC - Endpoint must be ONLINE (created in previous notebook)
# MAGIC - Embeddings table has data ✅
# MAGIC
# MAGIC **This will**:
# MAGIC - Create Delta Sync index with Databricks-managed embeddings
# MAGIC - Auto-generate vectors using `databricks-bge-large-en` model
# MAGIC - Sync incrementally when source table changes

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# Check endpoint status
endpoint_info = client.get_endpoint(name=VECTOR_ENDPOINT)
endpoint_state = endpoint_info.get('endpoint_status', {}).get('state', 'Unknown')

print(f"Vector Search Endpoint: {VECTOR_ENDPOINT}")
print(f"Status: {endpoint_state}")

if endpoint_state != "ONLINE":
    print(f"\n⚠️  Endpoint not ready. Current state: {endpoint_state}")
    print("   Please wait for endpoint to reach ONLINE state (5-10 minutes)")
    print("   Then re-run this cell to create the index")
else:
    print("✅ Endpoint is ONLINE - ready to create index")

# COMMAND ----------

# Create Vector Search Index (run only when endpoint is ONLINE)
if endpoint_state == "ONLINE":
    try:
        # Check if index already exists
        try:
            existing_index = client.get_index(name=VECTOR_INDEX_FQN)
            print(f"ℹ️  Vector index already exists: {VECTOR_INDEX_FQN}")
            print(f"   Deleting existing index to recreate...")
            client.delete_index(name=VECTOR_INDEX_FQN)
            print(f"   Deleted. Creating new index...")
        except:
            print(f"Creating new vector index: {VECTOR_INDEX_FQN}")

        # Create index with Databricks-managed embeddings
        index = client.create_delta_sync_index(
            endpoint_name=VECTOR_ENDPOINT,
            index_name=VECTOR_INDEX_FQN,
            source_table_name=f"{SCHEMA_AI_FQN}.ticket_embeddings",
            pipeline_type="TRIGGERED",
            primary_key="ticket_id",
            embedding_source_column="content",
            embedding_model_endpoint_name="databricks-bge-large-en"
        )

        print(f"✅ Vector Search index created: {VECTOR_INDEX_FQN}")
        print(f"   Source table: {SCHEMA_AI_FQN}.ticket_embeddings")
        print(f"   Embedding model: databricks-bge-large-en")
        print(f"   Sync mode: TRIGGERED")
        print(f"\n⏳ Index is syncing... (may take 2-5 minutes)")
        print(f"   Check status in Vector Search UI")

    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        print(f"   Check if:")
        print(f"   - Table {SCHEMA_AI_FQN}.ticket_embeddings has data")
        print(f"   - Endpoint {VECTOR_ENDPOINT} is ONLINE")
        print(f"   - You have CREATE permissions on {SCHEMA_AI_FQN}")
else:
    print("⚠️  Skipping index creation - endpoint not ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Data Loaded**:
# MAGIC - 100 support tickets → `ts_dlh_dev_catalog.data.tickets`
# MAGIC - 12 KB documents → `ts_dlh_dev_catalog.data.kb_documents`
# MAGIC - 12 embeddings → `ts_dlh_dev_catalog.assets.ticket_embeddings`
# MAGIC - 3 text files → `/Volumes/ts_dlh_dev_catalog/data/kb_docs_volume/`
# MAGIC
# MAGIC ✅ **Vector Index**: `ts_dlh_dev_catalog.assets.kb_vs_index`
# MAGIC
# MAGIC ## Next Steps
# MAGIC
# MAGIC 1. Wait for vector index sync to complete (check UI)
# MAGIC 2. Start **Topic 1: Vector DB** - Query the vector index
# MAGIC 3. Test similarity search
# MAGIC 4. Continue through 12 AI topics

# COMMAND ----------

print("=" * 60)
print("🎉 Sample Data Loaded Successfully!")
print("=" * 60)
print(f"\n📊 Data Summary:")
print(f"   - Tickets: 100")
print(f"   - KB Documents: 12")
print(f"   - Embeddings: 12")
print(f"   - Files in volume: 3")
print(f"\n🔍 Vector Index: {VECTOR_INDEX_FQN}")
print(f"   Status: Check Databricks UI > Machine Learning > Vector Search")
print(f"\n🚀 Ready to start learning!")
