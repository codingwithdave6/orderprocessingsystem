from src.order_service.repositories.implementation.ticket_repository import InMemoryTicketRepository
from src.order_service.repositories.interfaces.interfaces import TicketRepositoryInterface
from .payment_failed_processor import PaymentFailedProcessor


PROCESSOR_REGISTRY: dict[str, type] = {
    "paymentFailed": PaymentFailedProcessor,
}


def get_processor(event_type: str, ticket_repository: TicketRepositoryInterface):
    processor_class = PROCESSOR_REGISTRY.get(event_type)
    if processor_class is None:
        return None
    return processor_class(ticket_repository)
