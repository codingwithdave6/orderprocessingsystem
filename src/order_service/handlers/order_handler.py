from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.order_service.exceptions.order_exception import InvalidTransitionError, OrderNotFoundError
from src.order_service.models.order import Order
from src.order_service.repositories.implementation.order_repository import InMemoryOrderRepository
from src.order_service.repositories.implementation.ticket_repository import InMemoryTicketRepository
from src.order_service.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

_order_repository = InMemoryOrderRepository()
_ticket_repository = InMemoryTicketRepository()
_order_service = OrderService(_order_repository, _ticket_repository)


def get_order_service() -> OrderService:
    return _order_service


class CreateOrderRequest(BaseModel):
    product_ids: list[str] = Field(...)
    amount: float = Field(..., gt=0)


class TriggerEventRequest(BaseModel):
    event_type: str = Field(...)
    metadata: dict = Field(default_factory=dict)


@router.post("", response_model=Order, status_code=201)
def create_order(request: CreateOrderRequest, service: OrderService = Depends(get_order_service)) -> Order:
    try:
        return service.create_order(request.product_ids, request.amount)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{order_id}/events", response_model=Order)
def trigger_event(order_id: str, request: TriggerEventRequest, service: OrderService = Depends(get_order_service)) -> Order:
    try:
        return service.process_event(order_id, request.event_type, request.metadata)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, service: OrderService = Depends(get_order_service)) -> Order:
    try:
        return service.get_order(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
