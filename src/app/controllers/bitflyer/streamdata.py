from functools import partial
import logging
from threading import Lock
from threading import Thread

from app.controllers.bitflyer.ai import AI
from app.models.candle import create_candle_with_duration
from app.models.candle import create_initial_candle_with_duration
from bitflyer.bitflyer import Ticker
from bitflyer.bitflyer import RealtimeAPI

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

from bitflyer.bitflyer import APIClient
api = APIClient(settings.bitflyer_api_key, settings.bitflyer_api_secret)


class StreamData(object):

    def __init__(self):
        self.ai = AI()
        self.trade_lock = Lock()
            
#     def stream_ingestion_data(self):
#         trade_with_ai = partial(self.trade, ai=self.ai)
#         api.get_realtime_ticker(settings.product_code, callback=trade_with_ai)


    def stream_ingestion_data(self):
        trade_with_ai = partial(self.trade, ai=self.ai)
        url = settings.bitflyer_realtime_api_end_point
        channel = settings.bitflyer_realtime_ticker_product_code
        json_rpc = RealtimeAPI(url=url, channel=channel, callback=trade_with_ai)

    def trade(self, ticker: Ticker, ai: AI):
        for duration in constants.DURATIONS:
            if not (duration == settings.trade_duration):
                continue
            is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
            if duration == settings.trade_duration:
                thread = Thread(target=self._trade, args=(ai,is_created))
                thread.start()

    def _trade(self, ai: AI, is_created):
        with self.trade_lock:
            ai.trade(is_created)

stream = StreamData()
