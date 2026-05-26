from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.order_service.exceptions.order_exception import InvalidTransitionError, OrderNotFoundError
from src.order_service.handlers.order_handler import router

app = FastAPI(title="Order Processing Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(OrderNotFoundError)
async def order_not_found_exception_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidTransitionError)
async def invalid_transition_exception_handler(request: Request, exc: InvalidTransitionError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.order_service.main:app", host="0.0.0.0", port=8000, reload=True)
