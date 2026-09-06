from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.order_book import OrderBook


app = FastAPI(title="Order Book API")

book = OrderBook()


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class PriceLevel(BaseModel):
    price: float
    qty: int


class OrderBookResponse(BaseModel):
    bids: list[PriceLevel]
    asks: list[PriceLevel]


class OrderRequest(BaseModel):
    side: OrderSide
    type: OrderType
    price: float | None = None
    qty: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_price(self):
        if self.type == OrderType.LIMIT:
            if self.price is None:
                raise ValueError("Limit orders require a price")

            if self.price <= 0:
                raise ValueError("Limit order price must be greater than 0")

        return self


class OrderResponse(BaseModel):
    id: int
    side: OrderSide
    type: OrderType
    price: float | None
    qty: int
    fill_qty: int
    status: str


class TradeResponse(BaseModel):
    id: int
    price: float
    qty: int
    buy_id: int
    sell_id: int

@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(request: OrderRequest):
    order = book.add_order(
        side=request.side.value,
        price=request.price,
        qty=request.qty
    )

    return OrderResponse(
        id=order.id,
        side=order.side,
        type=request.type,
        price=order.price,
        qty=order.qty,
        fill_qty=order.fill_qty,
        status=order.status
    )


@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int):
    order = book.orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    return OrderResponse(
        id=order.id,
        side=order.side,
        type=OrderType.LIMIT,
        price=order.price,
        qty=order.qty,
        fill_qty=order.fill_qty,
        status=order.status
    )


@app.delete("/orders/{order_id}", response_model=OrderResponse)
def cancel_order(order_id: int):
    try:
        order = book.cancel_order(order_id)

    except ValueError:
        raise HTTPException(
            status_code=409,
            detail="Order can not be cancelled"
        )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order Not Found"
        )

    return OrderResponse(
        id=order.id,
        side=order.side,
        type=OrderType.LIMIT,
        price=order.price,
        qty=order.qty,
        fill_qty=order.fill_qty,
        status=order.status
    )


@app.get("/orderbook", response_model=OrderBookResponse)
def get_orderbook():
    bid_levels = {}
    ask_levels = {}

    for order in book.bids:
        bid_levels[order.price] = (
            bid_levels.get(order.price, 0)
            + order.rem_qty
        )

    for order in book.asks:
        ask_levels[order.price] = (
            ask_levels.get(order.price, 0)
            + order.rem_qty
        )

    bids = [
        PriceLevel(price=price, qty=qty)
        for price, qty in sorted(
            bid_levels.items(),
            reverse=True
        )
    ]

    asks = [
        PriceLevel(price=price, qty=qty)
        for price, qty in sorted(
            ask_levels.items()
        )
    ]

    return OrderBookResponse(
        bids=bids,
        asks=asks
    )

@app.get("/trades", response_model=list[TradeResponse])
def get_trades():

    return [
        TradeResponse(
            id=trade.id,
            price=trade.price,
            qty=trade.qty,
            buy_id=trade.buy_id,
            sell_id=trade.sell_id
        )
        for trade in book.trades
    ]
