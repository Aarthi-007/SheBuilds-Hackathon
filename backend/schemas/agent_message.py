from pydantic import BaseModel, Field
from datetime import datetime


class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    payload: dict
    trace_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
