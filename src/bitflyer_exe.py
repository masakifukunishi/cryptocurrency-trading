import sys
from threading import Thread
import logging

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)

import settings.constants as constants
import settings.settings as settings


if __name__ == "__main__":
    if settings.environment == constants.ENVIRONMENT_DEV:
        from cryptowatch.cryptowatch import Candle
        from app.models.candle import create_backtest_candle_with_duration
        from app.controllers.bitflyer.ai import AI
        from bitflyer.bitflyer import APIClient

        ai = AI()
        API = APIClient(settings.bitflyer_api_key, settings.bitflyer_api_secret)
        duration_time = constants.TRADE_MAP[settings.trade_duration]['granularity']
        if duration_time in constants.CRYPTOWATCH_ENABLE_PERIOD:
            candle = Candle(duration_time)
            candles = candle.get_candles(settings.backtest_period)
            for candle in candles:
                create_backtest_candle_with_duration(settings.product_code, settings.trade_duration, candle)
                ai.trade(is_created=True)
        
    elif settings.environment == constants.ENVIRONMENT_PRODUCTION:
        from app.controllers.initialprocess import InitialProcess
        # from app.controllers.dataprocess import DataProcess

        initial = InitialProcess()
        initial.set_initial_candles()

#         data = DataProcess()
#         data.delete_candles_recursive()

        from app.controllers.bitflyer.streamdata import stream
        streamThread = Thread(target=stream.stream_ingestion_data)
        streamThread.start()
        streamThread.join()