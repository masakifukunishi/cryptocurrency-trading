from functools import partial
import logging
from threading import Lock
from threading import Thread

from app.controllers.ai import AI
from app.models.candle import create_candle_with_duration
from app.models.candle import create_initial_candle_with_duration
from bitflyer.bitflyer import Ticker
from bitflyer.bitflyer import RealtimeAPI
from cryptowatch.cryptowatch import Candle

import constants
import settings

logger = logging.getLogger(__name__)

from bitflyer.bitflyer import APIClient
api = APIClient(settings.api_key, settings.api_secret)


class StreamData(object):

    def __init__(self):
        self.ai = AI(
            product_code=settings.product_code,
            use_percent=settings.use_percent,
            duration=settings.trade_duration,
            past_period=settings.past_period,
            stop_limit_percent=settings.stop_limit_percent,
            environment=settings.environment)
        self.trade_lock = Lock()

    def set_initial_candles(self):
        for duration in constants.DURATIONS:
            duration_time = constants.TRADE_MAP[duration]['granularity']
            if duration_time in constants.CRYPTOWATCH_ENABLE_PERIOD:
                candle = Candle(duration_time)
                candles = candle.get_candles()
                create_initial_candle_with_duration(settings.product_code, duration, candles)
            
#     def stream_ingestion_data(self):
#         trade_with_ai = partial(self.trade, ai=self.ai)
#         api.get_realtime_ticker(settings.product_code, callback=trade_with_ai)


    def stream_ingestion_data(self):
        self.set_initial_candles()
        trade_with_ai = partial(self.trade, ai=self.ai)
        url = settings.realtime_api_end_point
        channel = settings.realtime_ticker_product_code
        json_rpc = RealtimeAPI(url=url, channel=channel, callback=trade_with_ai)

    def trade(self, ticker: Ticker, ai: AI):
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
