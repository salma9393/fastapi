from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(BaseModel):
    id: int = Field(..., gt=0, description="Order ID must be positive")
    item: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=1000)
    price: float = Field(..., gt=0)
    status: OrderStatus = OrderStatus.pending
    customer_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator('item')
    def item_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Item name cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator('price')
    def reasonable_price(cls, v):
        if v > 100000:
            raise ValueError("Price seems unreasonably high")
        return v

class OrderCreate(BaseModel):
    item: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=1000)
    price: float = Field(..., gt=0)
    customer_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    notes: Optional[str] = Field(None, max_length=500)

class OrderUpdate(BaseModel):
    item: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, gt=0, le=1000)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[OrderStatus] = None
    customer_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator('item')
    def non_empty_item(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Item name cannot be empty or whitespace")
        return v.strip() if v else v

app = FastAPI(
    title="Data Type Enforcement Demo",
    description="Demonstrates strict data validation and type enforcement"
)

orders: List[Order] = []
next_id = 1

@app.post("/orders/", response_model=Order)
def create_order(order_data: OrderCreate):
    global next_id

    order = Order(
        id=next_id,
        item=order_data.item,
        quantity=order_data.quantity,
        price=order_data.price,
        customer_email=order_data.customer_email,
        notes=order_data.notes
    )

    orders.append(order)
    next_id += 1
    return order

@app.get("/orders/", response_model=List[Order])
def get_orders(
    status: Optional[OrderStatus] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0)
):
    filtered = orders

    if status:
        filtered = [o for o in filtered if o.status == status]
    if min_price is not None:
        filtered = [o for o in filtered if o.price >= min_price]
    if max_price is not None:
        filtered = [o for o in filtered if o.price <= max_price]

    return filtered

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int = Path(..., gt=0)):
    for order in orders:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, update: OrderUpdate):
    for i, order in enumerate(orders):
        if order.id == order_id:
            update_data = update.model_dump(exclude_unset=True)
            updated_order = order.model_copy(update=update_data)
            orders[i] = updated_order
            return updated_order

    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    for i, order in enumerate(orders):
        if order.id == order_id:
            del orders[i]
            return {"message": f"Order {order_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Order not found")

@app.get("/")
def root():
    return {"message": "Data Type Enforcement Demo API running"}
