
class OrderNotFoundError(Exception):
    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order with id {order_id} not found")

class InvalidTransitionError(Exception):
    def __init__(self, current_state: str, event_type: str):
        self.current_state = current_state
        self.event_type = event_type
        super().__init__(f"Invalid transition from {current_state} via {event_type}")

class InvalidOrderDataError(Exception):
    pass