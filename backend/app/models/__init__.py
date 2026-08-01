from app.models.user import User, Organization
from app.models.brand import Brand, BrandAsset
from app.models.identity import BrandIdentity, AIMemory
from app.models.campaign import Campaign, CampaignVersion
from app.models.validation import ValidationReport
from app.models.optimization import OptimizationReport
from app.models.trend import TrendReport
from app.models.job import Job, AuditLog

all_models = [
    User,
    Organization,
    Brand,
    BrandAsset,
    BrandIdentity,
    AIMemory,
    Campaign,
    CampaignVersion,
    ValidationReport,
    OptimizationReport,
    TrendReport,
    Job,
    AuditLog
]
