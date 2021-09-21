import logging
import requests
import time
import pandas as pd
from datetime import datetime

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

class Candle(object):
    def __init__(self, preiods):
        self.url = settings.bitflyer_btcjpy_ohlc_url
        self.preiods = preiods
        self.query = {
            'periods': self.preiods,
            }
        
    def get_candles(self, period):
        resp_candles = requests.get(self.url, params=self.query).json()['result'][self.preiods]
        del resp_candles[-1]
        candles = resp_candles[-period:]
        return candles
