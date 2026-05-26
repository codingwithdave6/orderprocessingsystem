from datetime import datetime
from unittest.mock import Mock
import uuid

from src.order_service.event_processors.payment_failed_processor import PaymentFailedProcessor
from src.order_service.event_processors.processor_registry import get_processor
from src.order_service.models.order import Order, OrderStatus


def test_processor_creates_ticket_if_amount_gt_1000():
    mock_ticket_repo = Mock()
    processor = PaymentFailedProcessor(mock_ticket_repo)
    
    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["p1"],
        amount=1500.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    processor.process(order, {})
    
    mock_ticket_repo.save_ticket.assert_called_once()
    ticket = mock_ticket_repo.save_ticket.call_args[0][0]
    assert "1000 USD" in ticket.reason

def test_processor_does_nothing_if_amount_lte_1000():
    mock_ticket_repo = Mock()
    processor = PaymentFailedProcessor(mock_ticket_repo)
    order = Order(
        id=str(uuid.uuid4()),
        product_ids=[],
        amount=50.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    processor.process(order, {})
    mock_ticket_repo.save_ticket.assert_not_called()


def test_registry_returns_processor_for_payment_failed():
    mock_ticket_repo = Mock()
    processor = get_processor("paymentFailed", mock_ticket_repo)
    assert processor is not None
    assert isinstance(processor, PaymentFailedProcessor)


def test_registry_returns_none_for_unknown_event():
    assert get_processor("unknown", Mock()) is None