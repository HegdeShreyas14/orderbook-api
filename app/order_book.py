from app.models import Order, Trade

class OrderBook:

    def __init__(self):
        self.orders = {}
        self.bids = []
        self.asks = []
        self.next_orderid = 1
        self.trades = []
        self.next_tradeid = 1


    def add_order(self , side , price, qty):
        order = Order(id = self.next_orderid,side = side, price = price,qty = qty)

        self.next_orderid += 1
        self.orders[order.id] = order
        # best implementation of sorting would be to use price map + ordered prices and a FIFO queue at every price level
        if side == "buy":
            self._match_buy(order)
            if order.rem_qty > 0:
                self.bids.append(order)
                self.bids.sort(key = lambda x: -x.price)
        else:
            self._match_sell(order)
            if order.rem_qty > 0:
                self.asks.append(order)
                self.asks.sort(key = lambda x : x.price)

        return order

    def _match_buy(self , buy_order):
        while buy_order.rem_qty >0 and self.asks:
            best_ask = self.asks[0]

            if buy_order.price < best_ask.price:
                break

            trade_qty = min(buy_order.rem_qty , best_ask.rem_qty)

            buy_order.fill_qty += trade_qty
            best_ask.fill_qty += trade_qty

            trade = Trade(id = self.next_tradeid , price = best_ask.price , qty = trade_qty , buy_id = buy_order.id , sell_id = best_ask.id)

            self.next_tradeid += 1
            self.trades.append(trade)

            if best_ask.rem_qty == 0:
                best_ask.status = "filled"
                self.asks.pop(0)
            else:
                best_ask.status = "partially_filled"

        if buy_order.rem_qty == 0:
            buy_order.status = "filled"
        elif buy_order.fill_qty > 0:
            buy_order.status = "partially_filled"



    def _match_sell(self, sell_order):
        while sell_order.rem_qty > 0 and self.bids:

            best_bid = self.bids[0]

            if sell_order.price > best_bid.price:
                break

            trade_qty = min(sell_order.rem_qty,best_bid.rem_qty)

            sell_order.fill_qty += trade_qty
            best_bid.fill_qty += trade_qty

            trade = Trade(id=self.next_tradeid,price=best_bid.price, qty=trade_qty, buy_id=best_bid.id,sell_id=sell_order.id)

            self.next_tradeid += 1
            self.trades.append(trade)

            if best_bid.rem_qty == 0:
                best_bid.status = "filled"
                self.bids.pop(0)
            else:
                best_bid.status = "partially_filled"

        if sell_order.rem_qty == 0:
            sell_order.status = "filled"
        elif sell_order.fill_qty > 0:
            sell_order.status = "partially_filled"

    def cancel_order(self , order_id):
        order = self.orders.get(order_id)

        if order is None:
            return None

        if order.status in ("filled" , "cancelled"):
            raise ValueError("Order can not be cancelled")

        if order.side == "buy":
            if order in self.bids:
                self.bids.remove(order)

        else:
            if order in self.asks:
                self.asks.remove(order)

        order.status = "cancelled"

        return order
