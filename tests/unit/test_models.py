import pytest
from datetime import datetime
from uuid import UUID

from src.order_service.models.order import Order, OrderHistoryEntry, OrderStatus

def test_order_creation():
    """Test 1: Crear orden con estado inicial PENDING"""
    order = Order(
        id="123e4567-e89b-12d3-a456-426614174000",
        product_ids=["prod1", "prod2"],
        amount=150.50
    )
    
    assert order.id == "123e4567-e89b-12d3-a456-426614174000"
    assert order.product_ids == ["prod1", "prod2"]
    assert order.amount == 150.50
    assert order.status == OrderStatus.PENDING
    assert order.history == []
    assert isinstance(order.created_at, datetime)
    assert isinstance(order.updated_at, datetime)

def test_order_history_entry():
    """Test 2: Crear entrada de historial"""
    entry = OrderHistoryEntry(
        event_type="paymentSuccessful",
        from_state=OrderStatus.PENDING_PAYMENT,
        to_state=OrderStatus.CONFIRMED,
        metadata={"transaction_id": "tx123"}
    )
    
    assert entry.event_type == "paymentSuccessful"
    assert entry.from_state == OrderStatus.PENDING_PAYMENT
    assert entry.to_state == OrderStatus.CONFIRMED
    assert entry.metadata["transaction_id"] == "tx123"
    assert isinstance(entry.timestamp, datetime)

def test_order_status_enum():
    """Test 3: Verificar todos los estados requeridos"""
    estados_esperados = [
        "PENDING", "ON_HOLD", "PENDING_PAYMENT", "CONFIRMED",
        "PROCESSING", "SHIPPED", "DELIVERED", "RETURNING",
        "RETURNED", "REFUNDED", "CANCELLED"
    ]
    
    for estado in estados_esperados:
        assert hasattr(OrderStatus, estado)
        assert isinstance(getattr(OrderStatus, estado), OrderStatus)