from app.order_book import OrderBook


def test_add_buy():
    book =  OrderBook()

    order = book.add_order(side = "buy" , price = 100 , qty = 10)

    assert order.id == 1
    assert order.side == "buy"
    assert order.price == 100
    assert order.qty == 10
    assert order.fill_qty == 0
    assert order.rem_qty == 10

def test_bid_priority():
    book = OrderBook()
    book.add_order("buy" , 100 , 10)
    book.add_order("buy" , 105 , 5)
    book.add_order("buy" , 102 , 7)

    assert book.bids[0].price == 105
    assert book.bids[1].price == 102
    assert book.bids[2].price == 100


def test_ask_priority():
    book = OrderBook()

    book.add_order("sell", 105, 5)
    book.add_order("sell", 100, 10)
    book.add_order("sell", 102, 7)

    assert book.asks[0].price == 100
    assert book.asks[1].price == 102
    assert book.asks[2].price == 105

def test_full_match():
    book = OrderBook()

    sell = book.add_order("sell", 100, 10)
    buy = book.add_order("buy", 100, 10)

    assert sell.status == "filled"
    assert buy.status == "filled"
    assert sell.fill_qty == 10
    assert buy.fill_qty == 10

    assert len(book.trades) == 1
    assert book.trades[0].price == 100
    assert book.trades[0].qty == 10

def test_partial_match():
    book = OrderBook()

    sell = book.add_order("sell", 100, 10)
    buy = book.add_order("buy", 100, 6)

    assert sell.status == "partially_filled"
    assert buy.status == "filled"

    assert sell.rem_qty == 4
    assert buy.rem_qty == 0

    assert len(book.trades) == 1
    assert book.trades[0].qty == 6

def test_match_multiple_orders():
    book = OrderBook()

    sell1 = book.add_order("sell", 100, 5)
    sell2 = book.add_order("sell", 101, 10)

    buy = book.add_order("buy", 102, 12)

    assert buy.status == "filled"
    assert buy.fill_qty == 12
    assert buy.rem_qty == 0

    assert sell1.status == "filled"
    assert sell1.fill_qty == 5

    assert sell2.status == "partially_filled"
    assert sell2.fill_qty == 7
    assert sell2.rem_qty == 3

    assert len(book.trades) == 2

    assert book.trades[0].price == 100
    assert book.trades[0].qty == 5

    assert book.trades[1].price == 101
    assert book.trades[1].qty == 7
