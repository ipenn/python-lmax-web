#coding=utf-8

from application.lmaxapi import *
import ast
import time

username = "ipenny12"
password = "wm150696"
type = "CFD_DEMO"

def main():
    api = lmaxapi()
    api.login(username,password,type)
    api.get_longpollkey()

    api.search_instruments()

    api.setup_subscription("order")
    api.subscribe_to_orderbook([4001,4004,4006])
    # 4001   EUR/USD
    # 4002   GBP/USD
    # 4003   EUR/GBP
    # 4004   USD/JPY
    # 4006   EUR/JPY
    print "get data start"
    #order_id = api.place_order(4003, order_type.market, fill_strategy.IoC,-1) # send order
    #order_id = api.close_order(4001,"AAAESQAAAAAE56oN", 1)
    
    while(1):
        result = api.get_events()
        if result:
            price = {}
            for update in result:
                if update.type == "orderbook":
                    if update.nbids > 0 and update.nasks > 0:
                        ask = ast.literal_eval(update.ask[0].price)
                        bid = ast.literal_eval(update.bid[0].price)
                        price[update.instrument_id] = [ask,bid]
                    else:
                        print "no bids and/or asks"
                if len(price) == 3:
                    v = price["4001"][1]*price["4004"][1]-price["4006"][0]
                    k = price["4001"][0]*price["4004"][0]-price["4006"][1]
                    if v > 0:
                        t0 = time.clock()
                        str = "SELL SELL BUY : ",v," = ",price["4001"][1]," * ",price["4004"][1]," - ",price["4006"][0]
                        log(str)
                        api.place_order(4001, order_type.market, fill_strategy.IoC, -0.8)
                        api.place_order(4004, order_type.market, fill_strategy.IoC, -0.8)
                        api.place_order(4006, order_type.market, fill_strategy.IoC, 0.8)
                        t1 = time.clock()
                        log(t1 - t0)
                    if k < 0:
                        t0 = time.clock()
                        str = "BUY BUY SELL : ", k," = ",price["4001"][0]," * ",price["4004"][0]," - ",price["4006"][1]
                        log(str)
                        api.place_order(4001, order_type.market, fill_strategy.IoC, 0.8)
                        api.place_order(4004, order_type.market, fill_strategy.IoC, 0.8)
                        api.place_order(4006, order_type.market, fill_strategy.IoC, -0.8)
                        t1 = time.clock()
                        log(t1 - t0)

    #api.search_instruments()




if __name__ == "__main__":
    main()