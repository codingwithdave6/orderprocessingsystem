from typing import List

from src.order_service.models.ticket import SupportTicket
from src.order_service.repositories.interfaces.interfaces import TicketRepositoryInterface


class InMemoryTicketRepository(TicketRepositoryInterface):
    def __init__(self):
        self._store: dict[str, List[SupportTicket]] = {}

    def save_ticket(self, ticket: SupportTicket) -> SupportTicket:
        if ticket.order_id not in self._store:
            self._store[ticket.order_id] = []
        self._store[ticket.order_id].append(ticket)
        return ticket

    def get_tickets_by_order_id(self, order_id: str) -> List[SupportTicket]:
        return self._store.get(order_id, [])