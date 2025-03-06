import random
import threading

class tradingEngine:
    listOfTickerSymbols = ["AMD", "GOOGL", "COST", "MSFT", "TSLA", "GM", "AMZN", "NVDA", "TGT", "NFLX", "META", "APPL", "INTC", "WMT", "CVS"]

    class Order:
        def __init__(self, orderType, tickerSymbol, quantity, price):
            self.orderType = orderType
            self.tickerSymbol = tickerSymbol
            self.quantity = quantity
            self.price = price

    def __init__(self):
        self.buyOrders = []
        self.sellOrders = []
        self.matchedOrders = []
        self.lock = threading.Lock()

    def addOrder(self, orderType, tickerSymbol, quantity, price):
        if len(self.buyOrders) + len(self.sellOrders) >= 1024:
            print("Maximum tickers have been traded.")
            return
        
        order = self.Order(orderType, tickerSymbol, quantity, price)
        if orderType == 'Buy':
            self.insertOrder(self.buyOrders, order)
        elif orderType == 'Sell':
            self.insertOrder(self.sellOrders, order)
        else:
            raise ValueError("Invalid order type. Must be 'Buy' or 'Sell'.")
    
    def insertOrder(self, orderList, order):
        i = 0
        while i < len(orderList):
            if orderList[i].tickerSymbol > order.tickerSymbol or (orderList[i].price > order.price and orderList[i].tickerSymbol == order.tickerSymbol):
                break
            else:
                i += 1
        orderList.insert(i, order)


    def callRandomOrder(self):
        orderType = random.choice(['Buy', 'Sell'])
        tickerSymbol = random.choice(self.listOfTickerSymbols)
        quantity = random.randint(1,100)
        price = round(random.uniform(1.0, 100.0), 2)
        self.addOrder(orderType, tickerSymbol, quantity, price)

    def matchOrder(self):
        buyIndex = 0
        sellIndex = 0

        while True:
            with self.lock:
                if buyIndex >= len(self.buyOrders) or sellIndex >= len(self.sellOrders):
                    return

                buy = self.buyOrders[buyIndex]
                sell = self.sellOrders[sellIndex]

                if buy.tickerSymbol == sell.tickerSymbol:
                    if buy.price >= sell.price:
                        quantity = min(buy.quantity, sell.quantity)

                        self.matchedOrders.append([buy.tickerSymbol, buy.price, sell.price, quantity])

                        if buy.quantity > sell.quantity:
                            buy.quantity -= sell.quantity
                            self.sellOrders.pop(sellIndex)
                        elif buy.quantity < sell.quantity:
                            sell.quantity -= buy.quantity
                            self.buyOrders.pop(buyIndex)
                        else:
                            self.buyOrders.pop(buyIndex)
                            self.sellOrders.pop(sellIndex)

                        if buy.quantity == 0:
                            buyIndex += 1
                        if sell.quantity == 0:
                            sellIndex += 1
                    else:
                        buyIndex += 1
                elif buy.tickerSymbol < sell.tickerSymbol:
                    buyIndex += 1
                else:
                    sellIndex += 1

if __name__ == "__main__":
    trading = tradingEngine()
    for i in range(1024):
        trading.callRandomOrder()

    threads = []
    for _ in range(5):
        t = threading.Thread(target=trading.matchOrder)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(len(trading.matchedOrders))
    for i in range(len(trading.matchedOrders)):
        print(trading.matchedOrders[i])
        
