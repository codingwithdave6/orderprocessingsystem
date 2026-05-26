from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field
import uuid

from src.order_service.models.ticket import SupportTicket

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ON_HOLD = "ON_HOLD"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    RETURNING = "RETURNING"
    RETURNED = "RETURNED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

class OrderHistoryEntry(BaseModel):
    event_type: str
    from_state: OrderStatus
    to_state: OrderStatus
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_ids: List[str]
    amount: float
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    history: List[OrderHistoryEntry] = Field(default_factory=list)
    tickets: List[SupportTicket] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)