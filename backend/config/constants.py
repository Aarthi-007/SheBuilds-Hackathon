EMBEDDING_DIMENSION = 1024
EMBEDDING_MODEL = "BAAI/bge-m3"

PINECONE_METRIC = "cosine"

# Workflow type identifiers
WORKFLOW_FULL_INGEST = "full_ingest"
WORKFLOW_QUICK_DRIFT = "quick_drift_check"
WORKFLOW_OPTIMIZE_ONLY = "optimize_only"
WORKFLOW_COMPETITOR_SCAN = "competitor_scan"

# Agent names
AGENT_PERCEPTION = "perception"
AGENT_BRAND_IDENTITY = "brand_identity"
AGENT_DRIFT = "drift"
AGENT_TREND = "trend"
AGENT_PREDICTION = "prediction"
AGENT_OPTIMIZATION = "optimization"
AGENT_COMPLIANCE = "compliance"
AGENT_COPYRIGHT = "copyright"
AGENT_SAFETY = "safety"
AGENT_CONTINUOUS_LEARNING = "continuous_learning"

# MongoDB collections
COL_UNIVERSAL_CONTENT = "universal_content"
COL_BRAND_IDENTITY = "brand_identity_models"
COL_BRAND_IDENTITY_HISTORY = "brand_identity_history"
COL_COMPETITOR_PROFILES = "competitor_profiles"
COL_TREND_KNOWLEDGE = "trend_knowledge"
COL_CAMPAIGN_MEMORY = "campaign_memory"
COL_DRIFT_REPORTS = "drift_reports"
COL_PREDICTION_REPORTS = "prediction_reports"
COL_OPTIMIZATION_REPORTS = "optimization_reports"
COL_COMPLIANCE_REPORTS = "compliance_reports"
COL_SAFETY_REPORTS = "safety_reports"
COL_COPYRIGHT_REPORTS = "copyright_reports"
COL_COMPANIES = "companies"
