from functools import partial
import logging

from app.models.candle import create_candle_with_duration
from bitflyer.bitflyer import Ticker

import constants
import settings

logger = logging.getLogger(__name__)

# TODO
from bitflyer.bitflyer import APIClient
api = APIClient(settings.api_key, settings.api_secret)


class StreamData(object):

    def stream_ingestion_data(self):
        api.get_realtime_ticker(settings.product_code, callback=self.trade)

    def trade(self, ticker: Ticker):
        logger.info(f'action=trade ticker={ticker.__dict__}')
        for duration in constants.DURATIONS:
            is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
            print(is_created)


# singleton
stream = StreamData()
