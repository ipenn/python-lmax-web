#coding=utf-8

from application.lmaxapi import *
import ast
import time
import multiprocessing
import os, random
username = "ipenny12"
password = "wm150696"
type = "CFD_DEMO"


api = lmaxapi()
api.login(username,password,type)
api.get_longpollkey()

api.search_instruments()

api.setup_subscription("order")
api.subscribe_to_orderbook([4001,4004,4006])


def place_order_1_buy():
    order_id = api.place_order(4001, order_type.market, fill_strategy.IoC, 0.8)


def place_order_1_sell():
    order_id = api.place_order(4001, order_type.market, fill_strategy.IoC, -0.8)


def place_order_2_buy():
    order_id = api.place_order(4004, order_type.market, fill_strategy.IoC, 0.8)


def place_order_2_sell():
    order_id = api.place_order(4004, order_type.market, fill_strategy.IoC, -0.8)


def place_order_3_buy():
    order_id = api.place_order(4006, order_type.market, fill_strategy.IoC, 0.8)

def place_order_3_sell():
    order_id = api.place_order(4006, order_type.market, fill_strategy.IoC, -0.8)

def poolssb():
    pool = multiprocessing.Pool(3)
    pool.apply_async(place_order_1_sell)
    pool.apply_async(place_order_2_sell)
    pool.apply_async(place_order_3_buy)
    pool.close()
    pool.join()

def poolbbs():
    pool = multiprocessing.Pool(3)
    pool.apply_async(place_order_1_buy)
    pool.apply_async(place_order_2_buy)
    pool.apply_async(place_order_3_sell)
    pool.close()
    pool.join()

def main():
    print "get data start"
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
                        poolssb()
                        t1 = time.clock()
                        log(t1 - t0)
                    if k < 0:
                        t0 = time.clock()
                        str = "BUY BUY SELL : ", k," = ",price["4001"][0]," * ",price["4004"][0]," - ",price["4006"][1]
                        log(str)
                        poolbbs()
                        t1 = time.clock()
                        log(t1 - t0)

    #api.search_instruments()


if __name__ == "__main__":
    main()