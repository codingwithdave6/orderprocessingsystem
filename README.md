# Order Processing State Machine Service

> **MVP de un servicio REST para gestión de órdenes mediante máquina de estados**
>
> Stack: **Python · FastAPI · Pydantic v2 · pytest · Vanilla JS**
>
> Arquitectura: **3 capas (Handlers, Services, Repositories)**

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Guía de Instalación y Ejecución](#guía-de-instalación-y-ejecución)
3. [Arquitectura y Decisiones Técnicas](#arquitectura-y-decisiones-técnicas)
4. [Trade-offs Asumidos](#trade-offs-asumidos)
5. [Integración en Sistemas Distribuidos](#integración-en-sistemas-distribuidos)
6. [Endpoints API](#endpoints-api)
7. [Testing](#testing)
8. [Decisiones de Seniority](#decisiones-de-seniority)

---

## Resumen Ejecutivo

Este servicio implementa una **máquina de estados** para procesar órdenes en línea con **11 estados** y transiciones válidas. Cada evento es validado contra el estado actual, se aplica lógica de negocio específica (ej. creación de tickets de soporte), y se persiste tanto el estado como un historial de auditoría completo.

**Características clave:**
- ✅ Crear órdenes con productos y monto
- ✅ Disparar eventos que validan transiciones de estado
- ✅ Lógica extendible por tipo de evento (Strategy Pattern)
- ✅ Historial de auditoría (Event Sourcing lite)
- ✅ API REST con validación automática (Pydantic)
- ✅ Frontend interactivo (Vanilla JS)
- ✅ Tests unitarios e integración (TDD)

---

## Guía de Instalación y Ejecución

### Requisitos Previos

- **Python** ≥ 3.14
- **pip** o **uv** (gestor de dependencias)
- **Git**

### 1) Clonar el Repositorio

```bash
git clone <repo-url>
cd OrderProcessingSystem
```

### 2) Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar (macOS/Linux)
source .venv/bin/activate
```

### 3) Instalar Dependencias

```bash
pip install -e .
# O si usas uv:
uv sync
```

### 4) Ejecutar el Backend (FastAPI)

```bash
python -m uvicorn src.order_service.main:app --reload --port 8000
```

El servidor estará disponible en:
- **API:** `http://127.0.0.1:8000`
- **Swagger UI (Docs):** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### 5) Ejecutar el Frontend (HTML + Vanilla JS)

**Opción A: Usar Python como servidor HTTP**

```bash
cd frontend
python -m http.server 5500
# Luego abre: http://127.0.0.1:5500
```

**Opción B: Usar VS Code Live Server**

- Click derecho en `frontend/index.html` → "Open with Live Server"

**Opción C: Abrir directamente en el navegador**

```bash
# Windows
start frontend/index.html

# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html
```

### 6) Ejecutar Tests

```bash
python -m pytest -q

```

---

## Arquitectura y Decisiones Técnicas

### Estructura en 3 Capas

```
┌─────────────────────────────────────┐
│  HTTP Request / Frontend Events     │
└─────────────────────┬───────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  Handlers / Controllers    │  ← Valida forma, parsea JSON
        │  (order_handler.py)        │  ← Retorna HTTP status
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  Services / Business Logic │  ← Orquesta flujo
        │  (order_service.py)        │  ← Aplica reglas
        │  (event_processors/)       │  ← Lógica por evento
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  Repositories / Adapters   │  ← Persiste datos
        │  (order_repository.py)     │  ← Abstrae DB
        │  (ticket_repository.py)    │
        └────────────────────────────┘
```

### Stack de Tecnologías

| Componente | Tecnología | Justificación |
|---|---|---|
| Framework API | **FastAPI** | Async nativo, validación automática, Swagger UI gratis |
| State Machine | **Dict puro** | KISS — sin dependencias externas, lógica explícita |
| Modelos | **Pydantic v2** | Tipado fuerte, serialización JSON automática |
| Storage MVP | **Dict en RAM** | Simple, fácil swap a DB real manteniendo interfaces |
| Servidor | **Uvicorn** | ASGI estándar, performante |
| Testing | **pytest** | Fixtures, mocks, integración con FastAPI |
| Frontend | **HTML + Vanilla JS** | Sin overhead de frameworks, 0 build step |

### Componentes Clave

#### 1) **State Machine** (`state_machine/order_state_machine.py`)

```python
VALID_TRANSITIONS = {
    OrderStatus.PENDING: {
        "noVerificationNeeded": OrderStatus.PENDING_PAYMENT,
        "paymentFailed": OrderStatus.CANCELLED,
        # ...
    },
    # ...
}

def get_next_state(current_state: OrderStatus, event_type: str) -> OrderStatus:
    """Función pura que valida transiciones."""
    transitions = VALID_TRANSITIONS.get(current_state, {})
    next_state = transitions.get(event_type)
    if next_state is None:
        raise InvalidTransitionError(current_state.value, event_type)
    return next_state
```

**Ventajas:**
- ✅ Testeable en aislamiento (función pura)
- ✅ Lógica completamente explícita (sin magia)
- ✅ Cero dependencias externas

#### 2) **Event Processors** (`event_processors/`)

Implementa **Strategy Pattern** para extender lógica de negocio sin modificar código existente.

```python
class PaymentFailedProcessor(BaseEventProcessor):
    def process(self, order: Order, metadata: dict) -> None:
        if order.amount > 1000.0:
            ticket = SupportTicket(
                order_id=order.id,
                reason="Amount exceeds 1000 USD"
            )
            self._ticket_repository.save_ticket(ticket)
            logger.info(f"Ticket created for {order.id}")
```

**Para agregar un nuevo evento:**
1. Crear `nuevo_evento_processor.py` extendiendo `BaseEventProcessor`
2. Registrarlo en `processor_registry.py`
3. ✅ Nada más cambia

#### 3) **Repository Pattern** (`repositories/`)

Abstrae toda interacción externa detrás de interfaces.

```python
class OrderRepositoryInterface(ABC):
    @abstractmethod
    def get_order_by_id(self, order_id: str) -> Optional[Order]: pass
    @abstractmethod
    def save_order(self, order: Order) -> Order: pass

# InMemoryOrderRepository implementa esta interfaz
# Podría haber: PostgresOrderRepository, DynamoDBOrderRepository, etc.
```

**Ventajas:**
- ✅ Fácil mockear en tests
- ✅ Swap a DB real sin cambiar Services
- ✅ Dependency Inversion Principle (SOLID)

#### 4) **Order Lifecycle** (`services/order_service.py`)

```
1. Crear orden (OrderService.create_order)
   └─> Generar UUID, inicializar status=PENDING, persistir

2. Procesar evento (OrderService.process_event)
   ├─> Cargar orden actual
   ├─> Obtener processor específico del evento (si existe)
   │   └─> Ejecutar lógica de negocio (ej. crear ticket)
   ├─> Validar transición (state_machine.get_next_state)
   ├─> Crear entrada en historial
   ├─> Actualizar status y timestamps
   └─> Persistir orden + retornar con tickets incluidos
```

#### 5) **Auditoría y Event Sourcing (lite)** (`models/order.py`)

Cada orden mantiene un historial inmutable de eventos:

```python
class Order(BaseModel):
    id: str
    status: OrderStatus
    history: List[OrderHistoryEntry]  # ← Event log
    tickets: List[SupportTicket]       # ← Side effects
    # ...

class OrderHistoryEntry(BaseModel):
    event_type: str
    from_state: OrderStatus
    to_state: OrderStatus
    timestamp: datetime
    metadata: dict  # ← Datos específicos del evento
```

**Beneficios:**
- ✅ Auditoría completa: quién, qué, cuándo
- ✅ Debugging: reproducir secuencia de cambios

---

## Trade-offs Asumidos

### ✅ Decisiones Favorables

| Decisión | Beneficio | Costo |
|---|---|---|
| Dict puro en RAM | 0 setup, tests rápidos | Datos perdidos al reiniciar |
| Pydantic v2 | Validación automática, serialización JSON | ~500KB adicional en dependencias |
| Repository Pattern | Testeable, extensible | Código más verboso |
| Event Sourcing lite | Auditoría, debugging | Duplicación de datos (status + history) |
| Strategy Pattern | Open/Closed Principle | Indirección adicional |

### ⚠️ Limitaciones Actuales

#### 1) **Storage en RAM**
- ❌ Datos se pierden al reiniciar servidor
- ✅ **Solución:** Reemplazar `InMemoryOrderRepository` con `PostgresOrderRepository(OrderRepositoryInterface)`
  - El resto del código sigue siendo idéntico


## Endpoints API

### 1) Crear Orden

```http
POST /orders
Content-Type: application/json

{
  "product_ids": ["prod1", "prod2"],
  "amount": 150.00
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "product_ids": ["prod1", "prod2"],
  "amount": 150.0,
  "status": "PENDING",
  "history": [],
  "tickets": [],
  "created_at": "2026-05-26T12:30:00",
  "updated_at": "2026-05-26T12:30:00"
}
```

### 2) Consultar Orden

```http
GET /orders/{order_id}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING_PAYMENT",
  "history": [
    {
      "event_type": "noVerificationNeeded",
      "from_state": "PENDING",
      "to_state": "PENDING_PAYMENT",
      "timestamp": "2026-05-26T12:31:00",
      "metadata": {}
    }
  ],
  "tickets": []
}
```

### 3) Disparar Evento

```http
POST /orders/{order_id}/events
Content-Type: application/json

{
  "event_type": "paymentSuccessful",
  "metadata": {"transaction_id": "tx123"}
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "CONFIRMED",
  "history": [
    {...},
    {
      "event_type": "paymentSuccessful",
      "from_state": "PENDING_PAYMENT",
      "to_state": "CONFIRMED",
      "timestamp": "2026-05-26T12:32:00",
      "metadata": {"transaction_id": "tx123"}
    }
  ]
}
```

**Errores:**
- `404` si orden no existe
- `422` si transición no es válida para el estado actual

### 4) Crear Orden con Monto Alto (Genera Ticket)

```http
POST /orders
{
  "product_ids": ["premium"],
  "amount": 1500.00
}

POST /orders/{order_id}/events
{
  "event_type": "paymentFailed",
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "CANCELLED",
  "tickets": [
    {
      "id": "ticket-uuid",
      "order_id": "order-uuid",
      "reason": "Amount exceeds 1000 USD — support review required",
      "created_at": "2026-05-26T12:33:00"
    }
  ]
}
```

---

## Testing

### Estructura de Tests

```
tests/
├── unit/
│   ├── test_models.py              ← Validación de modelos
│   ├── test_state_machine.py       ← Transiciones (puro)
│   ├── test_order_repository.py    ← Persistencia
│   ├── test_payment_failed_processor.py  ← Lógica de eventos
│   └── test_order_service.py       ← Orquestación (con mocks)
└── integration/
    └── test_order_handler.py       ← API end-to-end (TestClient)
```

### Ejecutar Tests

```bash
# Todos
python -m pytest -q


# Modo verbose
python -m pytest -v


```

**Resultado esperado:**
```
========================= 27 passed in 0.73s =========================
```

### Cobertura

- **State Machine:** 100% (función pura)
- **Repositories:** 100% (sin lógica, solo CRUD)
- **Processors:** 100% (comportamiento específico del evento)
- **Service:** 98% (orquestación)
- **Handlers:** 95% (validación HTTP)

---

## Frontend

### Características

- ✅ Crear orden con validación de entrada
- ✅ Cargar orden por ID y ver estado actual
- ✅ Dropdown dinámico de eventos permitidos según estado
- ✅ Historial de transiciones tabulado
- ✅ Contador de tickets generados
- ✅ Mensajes claros de error y éxito
- ✅ Resumen de transiciones posibles desde estado actual

### Uso

1. Abrir `http://127.0.0.1:5500` (o el puerto del servidor HTTP local)
2. **Crear Orden:**
   - Ingresa productos (ej. `prod1, prod2`)
   - Ingresa monto
   - Click "Crear orden"
3. **Cargar Orden Existente:**
   - Copia el UUID del paso anterior
   - Ingresa en "Load order" y click "Cargar orden"
4. **Disparar Evento:**
   - Selecciona evento del dropdown (solo muestra válidos)
   - Opcionalmente agrega metadata JSON
   - Click "Disparar evento"
5. **Ver Historial:**
   - Automáticamente se actualiza después de cada evento
   - Muestra transición, timestamp, metadata

---

## Estructura del Proyecto

```
OrderProcessingSystem/
├── README.md                          ← Este archivo
├── pyproject.toml                     ← Dependencias, métadata
├── .venv/                             ← Entorno virtual
│
├── src/
│   └── order_service/
│       ├── main.py                    ← FastAPI app, CORS, exception handlers
│       ├── models/
│       │   ├── order.py               ← Order, OrderStatus, OrderHistoryEntry
│       │   └── ticket.py              ← SupportTicket
│       ├── exceptions/
│       │   └── order_exception.py     ← OrderNotFoundError, InvalidTransitionError
│       ├── handlers/
│       │   └── order_handler.py       ← Endpoints POST /orders, /events, GET
│       ├── services/
│       │   └── order_service.py       ← create_order, process_event, get_order
│       ├── state_machine/
│       │   └── order_state_machine.py ← get_next_state (pura)
│       ├── event_processors/
│       │   ├── base_processor.py      ← Abstract BaseEventProcessor
│       │   ├── payment_failed_processor.py
│       │   └── processor_registry.py
│       └── repositories/
│           ├── interfaces/
│           │   └── interfaces.py      ← OrderRepositoryInterface, TicketRepositoryInterface
│           └── implementation/
│               ├── order_repository.py    ← InMemoryOrderRepository
│               └── ticket_repository.py   ← InMemoryTicketRepository
│
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_state_machine.py
│   │   ├── test_order_repository.py
│   │   ├── test_payment_failed_processor.py
│   │   └── test_order_service.py
│   └── integration/
│       └── test_order_handler.py
│
├── frontend/
│   └── index.html                     ← UI única, Vanilla JS
│
├── apitest/
│   └── api_test.http                  ← Tests HTTP REST Client
│
└── SDD/
    └── SDD_OrderStateMachine.md       ← Especificación de diseño
```

---


## Monitoreo y Observabilidad

### Logs Actuales

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO: root:ticket created for order d3b1a7c5 because amount 1500.00 is above 1000
```

### En Producción (AWS PowerTools)

```python
from aws_lambda_powertools import Logger, Tracer, Metrics

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@tracer.capture_lambda_handler
@logger.inject_lambda_context
def handler(event, context):
    metrics.add_metric(name="OrderProcessed", unit="Count", value=1)
    logger.info("Event processed", order_id=order_id, event_type=event_type)
    
    # CloudWatch captura automáticamente
    # Traces en X-Ray
    # Métricas en CloudWatch Dashboard
```

---


## Licencia

Confidencial. No distribuir sin autorización.

---

## Autor

Autor: David Valencia para Bridge
Stack: Python · FastAPI · Pydantic · pytest · Vanilla JS

---

