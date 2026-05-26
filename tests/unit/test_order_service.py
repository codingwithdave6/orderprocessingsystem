import pytest
from datetime import datetime
import uuid
from unittest.mock import Mock

from src.order_service.exceptions.order_exception import InvalidTransitionError, OrderNotFoundError
from src.order_service.models.order import Order, OrderStatus
from src.order_service.repositories.interfaces.interfaces import OrderRepositoryInterface, TicketRepositoryInterface
from src.order_service.services.order_service import OrderService


class DummyOrderRepository(OrderRepositoryInterface):
    def __init__(self):
        self.saved = None
        self.store = {}

    def get_order_by_id(self, order_id: str):
        return self.store.get(order_id)

    def save_order(self, order: Order):
        self.store[order.id] = order
        self.saved = order
        return order

    def list_orders(self):
        return list(self.store.values())


class DummyTicketRepository(TicketRepositoryInterface):
    def __init__(self):
        self.tickets = []

    def save_ticket(self, ticket):
        self.tickets.append(ticket)
        return ticket

    def get_tickets_by_order_id(self, order_id: str):
        return [ticket for ticket in self.tickets if ticket.order_id == order_id]


def test_create_order_returns_pending_and_saves():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    order = service.create_order(["prod1"], 200.0)

    assert order.status == OrderStatus.PENDING
    assert order.id in order_repo.store
    assert order_repo.saved == order


def test_get_order_returns_existing_order():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["prod1"],
        amount=100.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    order_repo.save_order(order)

    retrieved = service.get_order(order.id)
    assert retrieved == order


def test_get_order_raises_not_found_for_missing_order():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    with pytest.raises(OrderNotFoundError):
        service.get_order("missing")


def test_process_event_valid_transition_updates_status_and_history():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["prod1"],
        amount=100.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    order_repo.save_order(order)

    updated = service.process_event(order.id, "noVerificationNeeded", {"foo": "bar"})

    assert updated.status == OrderStatus.PENDING_PAYMENT
    assert len(updated.history) == 1
    assert updated.history[0].event_type == "noVerificationNeeded"
    assert updated.history[0].from_state == OrderStatus.PENDING
    assert updated.history[0].to_state == OrderStatus.PENDING_PAYMENT


def test_process_event_raises_not_found_for_unknown_order():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    with pytest.raises(OrderNotFoundError):
        service.process_event("missing", "paymentFailed", {})


def test_process_event_raises_invalid_transition():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["prod1"],
        amount=100.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    order_repo.save_order(order)

    with pytest.raises(InvalidTransitionError):
        service.process_event(order.id, "itemDispatched", {})


def test_process_event_payment_failed_creates_ticket_for_large_amount():
    order_repo = DummyOrderRepository()
    ticket_repo = DummyTicketRepository()
    service = OrderService(order_repo, ticket_repo)

    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["prod1"],
        amount=1500.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    order_repo.save_order(order)

    result = service.process_event(order.id, "paymentFailed", {})

    assert result.status == OrderStatus.CANCELLED
    assert len(ticket_repo.tickets) == 1
    assert ticket_repo.tickets[0].order_id == order.id
