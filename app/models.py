from dataclasses import dataclass
@dataclass
class Order:
    id:int
    side:str
    price:float
    qty:int
    fill_qty:int = 0
    status: str = "open"

    @property
    def rem_qty(self):
        return self.qty - self.fill_qty

@dataclass
class Trade:
    id:int
    price:float
    qty:int
    buy_id:int
    sell_id:int
