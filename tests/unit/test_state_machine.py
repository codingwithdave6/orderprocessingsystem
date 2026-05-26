import pytest
from src.order_service.exceptions.order_exception import InvalidTransitionError
from src.order_service.models.order import OrderStatus
from src.order_service.state_machine.order_state_machine import get_next_state

def test_valid_transition_returns_correct_state():
    assert get_next_state(OrderStatus.PENDING, "noVerificationNeeded") == OrderStatus.PENDING_PAYMENT

def test_invalid_transition_raises_error():
    with pytest.raises(InvalidTransitionError):
        get_next_state(OrderStatus.PENDING, "randomEvent")

def test_cancel_in_pending():
    assert get_next_state(OrderStatus.PENDING, "orderCancelledByUser") == OrderStatus.CANCELLED

def test_cancel_in_on_hold():
    assert get_next_state(OrderStatus.ON_HOLD, "orderCancelledByUser") == OrderStatus.CANCELLED

def test_cancel_fails_in_delivered():
    with pytest.raises(InvalidTransitionError):
        get_next_state(OrderStatus.DELIVERED, "orderCancelledByUser")

def test_cancel_fails_in_returned():
    with pytest.raises(InvalidTransitionError):
        get_next_state(OrderStatus.RETURNED, "orderCancelledByUser")

def test_cancel_fails_in_refunded():
    with pytest.raises(InvalidTransitionError):
        get_next_state(OrderStatus.REFUNDED, "orderCancelledByUser")