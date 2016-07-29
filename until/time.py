# -*- coding:utf-8 -*-
import datetime

def date(datefmt = "%Y-%m-%d",times = 0):
    if not times:
        times = datetime.datetime.now()

    return times.strftime(datefmt)

def strtotime(datefmt,timestr):
    return datetime.datetime.strptime('2015-03-05 17:41:20', '%Y-%m-%d %H:%M:%S')




