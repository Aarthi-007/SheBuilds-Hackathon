"""
CompanyRepository — reads the `companies` collection (context.md §10 tenant root).
Note: added `industry_keywords` to the Company doc — a short list of terms used to
build each company's News API query for the Trends & Opportunities scheduler job.
"""

from pydantic import BaseModel
from database.mongo_client import get_db


class Company(BaseModel):
    company_id: str
    name: str
    industry: str
    industry_keywords: list[str] = []   # e.g. ["running shoes", "sportswear", "athleisure"]


class CompanyRepository:
    def __init__(self):
        self._db = get_db()

    async def list_all(self) -> list[Company]:
        cursor = self._db.companies.find({})
        return [Company(**doc) async for doc in cursor]
