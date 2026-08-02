from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class TrendSignal(BaseModel):
    """One raw trend picked up from the News API, before it's judged as an opportunity."""
    signal_id: str
    company_id: str
    headline: str
    summary: str
    source: str
    url: str
    published_at: datetime
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    flattened_text: str          # headline + summary, used for embedding
    embedding_id: str | None = None   # id of the vector once upserted to Pinecone


class TrendKnowledge(BaseModel):
    company_id: str
    industry_trends: list[str]
    emerging_topics: list[str]
    competitor_campaigns: list[dict]
    trending_hashtags: list[str]
    seasonal_events: list[dict]
    fetched_at: datetime


class TrendMatch(BaseModel):
    """Output of the similarity-search step: a trend signal that scored close enough
    to the company's brand/campaign vectors to be worth judging."""
    signal: TrendSignal
    similarity_score: float                 # 0-1, cosine similarity from Pinecone
    matched_against: Literal["brand_identity", "campaign"]
    matched_id: str                         # company_id namespace vector id / campaign_id
