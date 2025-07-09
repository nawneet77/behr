from pydantic import BaseModel, Field
from typing import Optional, List

class GA4QueryInput(BaseModel):
    user_id: str = Field(..., description="User ID to identify whose GA4 tokens to use")
    dimensions: List[str] = Field(..., description="GA4 dimension names (e.g., ['date', 'country', 'pagePath'])")
    metrics: List[str] = Field(..., description="GA4 metric names (e.g., ['sessions', 'pageviews', 'users'])")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format (e.g., '2024-01-01')")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format (e.g., '2024-01-31')")
    limit: Optional[int] = Field(100, description="Maximum number of rows to return (default: 100)")
    property_id: Optional[str] = Field(None, description="Override GA4 property ID if needed")

class BasicQueryInput(BaseModel):
    user_id: str = Field(..., description="User ID to identify whose GA4 tokens to use")