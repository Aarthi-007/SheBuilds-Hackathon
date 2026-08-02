from datetime import datetime
from pydantic import BaseModel


class CampaignRecommendation(BaseModel):
    title: str
    angle: str                 # the creative/brand angle tying trend to brand identity
    suggested_formats: list[str]   # e.g. ["social post", "blog", "ad"]
    urgency: str                # e.g. "act within 48h", "evergreen"


class OpportunityReport(BaseModel):
    report_id: str
    company_id: str
    signal_id: str              # TrendSignal.signal_id this report judges
    is_opportunity: bool
    confidence: float           # 0-1, Claude's confidence in its own judgment
    reasoning: str               # why this is/isn't a good fit for the brand
    brand_fit_score: float       # 0-1, how well the trend aligns with brand identity
    recommendations: list[CampaignRecommendation]
    created_at: datetime


class TrackOpportunitiesRequest(BaseModel):
    """Input to OpportunityAgent.run(). One call = one tracking pass for one company."""
    company_id: str
    industry_keywords: list[str]        # e.g. ["running shoes", "sportswear"] — builds the News API query
    similarity_threshold: float = 0.75  # below this, a trend is considered unrelated and skipped


class TrackOpportunitiesResult(BaseModel):
    company_id: str
    signals_fetched: int
    matches_found: int
    opportunity_reports: list[OpportunityReport]
