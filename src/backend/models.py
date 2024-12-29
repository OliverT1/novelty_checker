from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ResearchPaper(BaseModel):
    """Model for a research paper returned by Exa"""

    id: str
    title: str
    url: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    summary: Optional[str] = None

    @validator("published_date", pre=True)
    def handle_empty_date(cls, v):
        if v == "" or v is None:
            return None
        return v


class ExasearchResponse(BaseModel):
    request_id: str
    resolved_search_type: str
    results: List[ResearchPaper]


class NoveltyCheckRequest(BaseModel):
    """Model for the novelty check request"""

    research_question: str = Field(..., min_length=10)


class NoveltyCheckResponse(BaseModel):
    """Model for the novelty check response"""

    novelty: str = Field(..., pattern="^(YES|NO)$")
    explanation: str
    papers: List[ResearchPaper] = Field(default_factory=list)
