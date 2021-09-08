import time

from app.models.candle import delete_candle
import settings.settings as settings
import settings.constants as constants

class DataProcess(object):
    def delete_candles_recursive(self):
        for duration in constants.DURATIONS:
            if not (duration == settings.trade_duration):
                continue
            delete_candle(settings.product_code, duration)
        time.sleep(settings.execute_delete_candle_duration)
        self.delete_candles_recursive()