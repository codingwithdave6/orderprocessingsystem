from datetime import datetime
from typing import Optional

from src.order_service.exceptions.order_exception import InvalidTransitionError, OrderNotFoundError
from src.order_service.event_processors.processor_registry import get_processor
from src.order_service.models.order import Order, OrderHistoryEntry
from src.order_service.repositories.interfaces.interfaces import OrderRepositoryInterface, TicketRepositoryInterface
from src.order_service.state_machine.order_state_machine import get_next_state


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepositoryInterface,
        ticket_repo: TicketRepositoryInterface,
    ):
        self._order_repo = order_repo
        self._ticket_repo = ticket_repo

    def create_order(self, product_ids: list[str], amount: float) -> Order:
        order = Order(product_ids=product_ids, amount=amount)
        return self._order_repo.save_order(order)

    def get_order(self, order_id: str) -> Order:
        order = self._order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        order.tickets = self._ticket_repo.get_tickets_by_order_id(order.id)
        return order

    def process_event(self, order_id: str, event_type: str, metadata: Optional[dict] = None) -> Order:
        metadata = metadata or {}
        order = self._order_repo.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        processor = get_processor(event_type, self._ticket_repo)
        if processor is not None:
            processor.process(order, metadata)

        previous_status = order.status
        next_status = get_next_state(order.status, event_type)
        order.status = next_status
        order.history.append(
            OrderHistoryEntry(
                event_type=event_type,
                from_state=previous_status,
                to_state=next_status,
                metadata=metadata,
            )
        )
        order.updated_at = datetime.now()
        self._order_repo.save_order(order)
        order.tickets = self._ticket_repo.get_tickets_by_order_id(order.id)
        return order
