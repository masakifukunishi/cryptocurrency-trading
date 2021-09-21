import sys
from threading import Thread
import logging

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)

import settings.constants as constants
import settings.settings as settings

if __name__ == "__main__":
    if settings.environment == constants.ENVIRONMENT_DEV:
        from app.controllers.gmo.ai import AI
        from app.models.candle import create_backtest_candle_with_duration
        from gmo.gmo import APIClient
        
        ai = AI()
        API = APIClient(settings.gmo_api_key, settings.gmo_api_secret)
        duration_time = constants.TRADE_MAP[settings.trade_duration]['duration']
        if duration_time in constants.GMO_ENABLE_PERIOD:
            candles = API.get_initial_candles(settings.backtest_period)
            for candle in candles:
                create_backtest_candle_with_duration(settings.product_code, settings.trade_duration, candle)
                ai.trade(is_created=True)
                
    elif settings.environment == constants.ENVIRONMENT_PRODUCTION:
        from app.controllers.gmo.streamdata import stream
        
        streamThread = Thread(target=stream.stream_ingestion_data)
        streamThread.start()
        streamThread.join()