from dataclasses import dataclass

@dataclass
class Order:
    id:int
    side:str
    price:float
    qty:int
    fill_qty:int = 0

    @property
    def rem_qty(self):
        return self.qty - self.fill_qty


class OrderBook:

    def __init__(self):
        self.orders = {}
        self.bids = []
        self.asks = []
        self.next_orderid = 1
        self.trades = []


    def add_order(self , side , price, qty):
        order = Order(
            id = self.next_orderid,
            side = side,
            price = price,
            qty = qty
        )

        self.next_orderid += 1
        self.orders[order.id] = order
        # best implementation of sorting would be to use price map + ordered prices and a FIFO queue at every price level
        if side == "buy":
            self.bids.append(order)
            self.bids.sort(key = lambda x: -x.price)
        else:
            self.asks.append(order)
            self.asks.sort(key = lambda x : x.price)

        return order
