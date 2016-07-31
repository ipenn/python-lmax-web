# coding: utf-8
import os

# 4001   EUR/USD
# 4002   GBP/USD
# 4003   EUR/GBP
# 4004   USD/JPY
# 4006   EUR/JPY

class Config(object):
    DEBUG = False
    instruments = {
        'EUR/USD': [80,0.1],
        'USD/JPY': [80, 0.1],
        'GBP/USD': [80, 0.1],
        'USD/CAD': [80, 0.1],
        'AUD/USD': [80, 0.1]
    }

