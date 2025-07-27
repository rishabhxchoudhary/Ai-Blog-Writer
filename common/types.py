from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Trend(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    source: str
    score: int
    ts: datetime
    
    def tuple(self):
        """Return tuple representation for database insertion"""
        return (self.id, self.title, self.url, self.source, self.score, self.ts)
