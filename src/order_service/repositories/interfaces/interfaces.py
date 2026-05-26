from abc import ABC, abstractmethod
from typing import List, Optional

from src.order_service.models.order import Order
from src.order_service.models.ticket import SupportTicket


class OrderRepositoryInterface(ABC):
    @abstractmethod
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        pass

    @abstractmethod
    def save_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    def list_orders(self) -> List[Order]:
        pass

class TicketRepositoryInterface(ABC):
    @abstractmethod
    def save_ticket(self, ticket: SupportTicket) -> SupportTicket:
        pass

    @abstractmethod
    def get_tickets_by_order_id(self, order_id: str) -> List[SupportTicket]:
        pass