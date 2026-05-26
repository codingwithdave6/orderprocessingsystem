from typing import List, Optional

from src.order_service.models.order import Order
from src.order_service.repositories.interfaces.interfaces import OrderRepositoryInterface


class InMemoryOrderRepository(OrderRepositoryInterface):
    def __init__(self):
        self._store: dict[str, Order] = {}

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        return self._store.get(order_id)

    def save_order(self, order: Order) -> Order:
        self._store[order.id] = order
        return order

    def list_orders(self) -> List[Order]:
        return list(self._store.values())