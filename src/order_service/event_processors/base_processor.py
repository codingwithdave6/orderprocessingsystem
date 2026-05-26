from abc import ABC, abstractmethod
from src.order_service.models.order import Order


class BaseEventProcessor(ABC):
    @abstractmethod
    def process(self, order: Order, metadata: dict) -> None:
        raise NotImplementedError
