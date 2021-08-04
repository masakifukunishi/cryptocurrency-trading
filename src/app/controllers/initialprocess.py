from cryptowatch.cryptowatch import Candle
from app.models.candle import create_initial_candle_with_duration

import settings.constants as constants
import settings.settings as settings

class InitialProcess(object):
    
    def set_initial_candles(self):
        for duration in constants.DURATIONS:
            duration_time = constants.TRADE_MAP[duration]['granularity']
            if duration_time in constants.CRYPTOWATCH_ENABLE_PERIOD:
                candle = Candle(duration_time)
                candles = candle.get_candles()
                create_initial_candle_with_duration(settings.product_code, duration, candles)