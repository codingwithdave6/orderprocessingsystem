import pytest
from datetime import datetime
import uuid

from src.order_service.models.order import Order, OrderStatus
from src.order_service.repositories.implementation.order_repository import InMemoryOrderRepository


@pytest.fixture
def repo():
    return InMemoryOrderRepository()

def test_save_and_get_order(repo):
    order = Order(
        id=str(uuid.uuid4()),
        product_ids=["p1"],
        amount=100.0,
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    saved = repo.save_order(order)
    assert repo.get_order_by_id(saved.id) == saved

def test_get_order_not_found(repo):
    assert repo.get_order_by_id("non-existent") is None