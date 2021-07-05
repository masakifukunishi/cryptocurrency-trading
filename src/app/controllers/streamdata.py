from functools import partial
import logging

from app.models.candle import create_candle_with_duration
from bitflyer.bitflyer import Ticker
from bitflyer.bitflyer import RealtimeAPI

import constants
import settings

logger = logging.getLogger(__name__)

# from bitflyer.bitflyer import APIClient
# api = APIClient(settings.api_key, settings.api_secret)


class StreamData(object):

#     def stream_ingestion_data(self):
#         api.get_realtime_ticker(settings.product_code, callback=self.trade)

#     def trade(self, ticker: Ticker):
#         logger.info(f'action=trade ticker={ticker.__dict__}')
#         for duration in constants.DURATIONS:
#             is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
#             print(is_created)

    def stream_ingestion_data(self):
        url = settings.realtime_api_end_point
        channel = settings.realtime_ticker_product_code
        json_rpc = RealtimeAPI(url=url, channel=channel, callback=self.trade)
        json_rpc.run()

    def trade(self, ticker: Ticker):
        logger.info(f'action=trade ticker={ticker.__dict__}')
        for duration in constants.DURATIONS:
            is_created = create_candle_with_duration(ticker.product_code, duration, ticker)
            print(is_created)
            
# singleton
stream = StreamData()
