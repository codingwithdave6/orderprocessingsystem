from datetime import datetime
from pydantic import BaseModel


class SupportTicket(BaseModel):
    id: str
    order_id: str
    reason: str
    created_at: datetime