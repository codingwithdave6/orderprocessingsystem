import logging
from datetime import datetime
from uuid import uuid4

from src.order_service.models.order import Order
from src.order_service.models.ticket import SupportTicket
from src.order_service.repositories.interfaces.interfaces import TicketRepositoryInterface
from .base_processor import BaseEventProcessor

logger = logging.getLogger(__name__)


class PaymentFailedProcessor(BaseEventProcessor):
    def __init__(self, ticket_repository: TicketRepositoryInterface):
        self._ticket_repository = ticket_repository

    def process(self, order: Order, metadata: dict) -> None:
        if order.amount <= 1000.0:
            return

        ticket = SupportTicket(
            id=str(uuid4()),
            order_id=order.id,
            reason="Amount exceeds 1000 USD — support review required",
            created_at=datetime.now(),
        )
        self._ticket_repository.save_ticket(ticket)
        logger.info(
            "ticket created for order %s because amount %.2f is above 1000",
            order.id,
            order.amount,
        )
