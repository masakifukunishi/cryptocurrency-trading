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
        self.ai = AI(
            product_code=settings.product_code,
            use_percent=settings.use_percent,
            duration=settings.trade_duration,
            past_period=settings.past_period,
            stop_limit_percent_sell=settings.stop_limit_percent_sell,
            stop_limit_percent_buy=settings.stop_limit_percent_buy,
            environment=settings.environment,
            fx_leverage=settings.fx_leverage,
            fx_actual_leverage=settings.fx_actual_leverage)
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
            if is_created and duration == settings.trade_duration:
                thread = Thread(target=self._trade, args=(ai,))
                thread.start()

    def _trade(self, ai: AI):
        with self.trade_lock:
            ai.trade()
# singleton
stream = StreamData()
