from src.order_service.exceptions.order_exception import InvalidTransitionError
from src.order_service.models.order import OrderStatus

VALID_TRANSITIONS = {
    OrderStatus.PENDING: {
        "pendingBiometricalVerification": OrderStatus.ON_HOLD,
        "noVerificationNeeded": OrderStatus.PENDING_PAYMENT,
        "paymentFailed": OrderStatus.CANCELLED,
        "orderCancelled": OrderStatus.CANCELLED,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.ON_HOLD: {
        "biometricalVerificationSuccessful": OrderStatus.PENDING_PAYMENT,
        "verificationFailed": OrderStatus.CANCELLED,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.PENDING_PAYMENT: {
        "paymentSuccessful": OrderStatus.CONFIRMED,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        "preparingShipment": OrderStatus.PROCESSING,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.PROCESSING: {
        "itemDispatched": OrderStatus.SHIPPED,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.SHIPPED: {
        "itemReceivedByCustomer": OrderStatus.DELIVERED,
        "deliveryIssue": OrderStatus.ON_HOLD,
        "orderCancelledByUser": OrderStatus.CANCELLED,
    },
    OrderStatus.DELIVERED: {
        "returnInitiatedByCustomer": OrderStatus.RETURNING,
    },
    OrderStatus.RETURNING: {
        "itemReceivedBack": OrderStatus.RETURNED,
    },
    OrderStatus.RETURNED: {
        "refundProcessed": OrderStatus.REFUNDED,
    },
    # Final states have no outgoing transitions
    OrderStatus.CANCELLED: {},
    OrderStatus.REFUNDED: {},
}

def get_next_state(current_state: OrderStatus, event_type: str) -> OrderStatus:
    transitions = VALID_TRANSITIONS.get(current_state, {})
    next_state = transitions.get(event_type)

    if next_state is None:
        raise InvalidTransitionError(current_state.value, event_type)

    return next_state