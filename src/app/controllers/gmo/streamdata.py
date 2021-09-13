from functools import partial
import logging
from threading import Lock
from threading import Thread

from app.controllers.gmo.ai import AI
from app.models.candle import create_candle_with_duration
from app.models.candle import create_initial_candle_with_duration
from gmo.gmo import Ticker
from gmo.gmo import RealtimeAPI

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)


class StreamData(object):

    def __init__(self):
        self.ai = AI()
        self.trade_lock = Lock()

    def stream_ingestion_data(self):
        trade_with_ai = partial(self.trade, ai=self.ai)
        url = settings.gmo_realtime_api_end_point
        channel = "ticker"
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
