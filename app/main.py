from enum import Enum
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel, Field ,model_validator
from app.order_book import OrderBook


app = FastAPI(title = "Order Book API")

book = OrderBook()

class OrderSide(str , Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str , Enum):
    LIMIT = "limit"
    MARKET = "market"

class OrderRequest(BaseModel):
    side:OrderSide
    type:OrderType
    price:float|None = None
    qty : int= Field(gt = 0)
    @model_validator(mode = "after")
    def validate_price(self):
        if self.type == OrderType.LIMIT:
            if self.price is None:
                raise ValueError("Limit Orders require a price")
            if self.price <= 0:
                raise ValueError("Orders need to have prices greater than 0")

        return self

class OrderResponse(BaseModel):
    id: int
    side: OrderSide
    type: OrderType
    price: float | None
    quantity: int
    filled_quantity: int
    status: str


@app.post("/orders" , response_model = OrderResponse , status_code = 201)
def create_order(request:OrderRequest):
    order = book.add_order(side = request.side.value , price = request.price , qty = request.qty)
    return OrderResponse(id=order.id,side=order.side,type=request.type,price=order.price,quantity=order.qty,filled_quantity=order.fill_qty,status=order.status)

@app.get("/order/{order_id}" , response_model = OrderResponse)
def get_order(order_id : int):
    order = book.orders.get(order_id)

    if order is None:
        raise HTTPException(status_code = 404 , detail = "Order Not Found")

    return OrderResponse(id = order.id , side = order.side , type = OrderType.LIMIT , price = order.price , quantity = order.qty , filled_quantity = order.fill_qty ,status = order.status)


@app.delete("/order/{order_id}" , response_model = OrderResponse):
def cancel_order(order_id:int):
    try:
        order = book.cancel_order(order_id)
    except ValueError:
        raise HTTPException(status_code = 409 , detail = "Order can not be cancelled")

    if order is None:
        raise HTTPException(status_code = 404 , detail = "Order Not Found")

    return OrderResponse(id=order.id,side=order.side,type=OrderType.LIMIT,price=order.price,quantity=order.qty,filled_quantity=order.fill_qty,status=order.status)
