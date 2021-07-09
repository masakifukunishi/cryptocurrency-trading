from functools import partial
import logging
from threading import Lock
from threading import Thread

from app.controllers.ai import AI
from app.models.candle import create_candle_with_duration
from bitflyer.bitflyer import Ticker
from bitflyer.bitflyer import RealtimeAPI

import constants
import settings

logger = logging.getLogger(__name__)

# from bitflyer.bitflyer import APIClient
# api = APIClient(settings.api_key, settings.api_secret)


class StreamData(object):

    def __init__(self):
        self.ai = AI(
            product_code=settings.product_code,
            use_percent=settings.use_percent,
            duration=settings.trade_duration,
            past_period=settings.past_period,
            stop_limit_percent=settings.stop_limit_percent,
            back_test=settings.back_test)
        self.trade_lock = Lock()
        
#     def stream_ingestion_data(self):
#         api.get_realtime_ticker(settings.product_code, callback=self.trade)

#     def trade(self, ticker: Ticker):
#         logger.info(f'action=trade ticker={ticker.__dict__}')
#         for duration in constants.DURATIONS:
#             is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
#             print(is_created)

    def stream_ingestion_data(self):
        trade_with_ai = partial(self.trade, ai=self.ai)
        url = settings.realtime_api_end_point
        channel = settings.realtime_ticker_product_code
        json_rpc = RealtimeAPI(url=url, channel=channel, callback=trade_with_ai)

    def trade(self, ticker: Ticker, ai: AI):
        logger.info(f'action=trade ticker={ticker.__dict__}')
        for duration in constants.DURATIONS:
            is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
            if is_created and duration == settings.trade_duration:
                thread = Thread(target=self._trade, args=(ai,))
                thread.start()

    def _trade(self, ai: AI):
        with self.trade_lock:
            ai.trade()
# singleton
stream = StreamData()
