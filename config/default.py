# coding: utf-8
import os

class Config(object):
    DEBUG = False
    instruments = {
        'EUR/USD': [80,0.1],
        'USD/JPY': [80, 0.1],
        'GBP/USD': [80, 0.1],
        'USD/CAD': [80, 0.1],
        'AUD/USD': [80, 0.1]
    }

