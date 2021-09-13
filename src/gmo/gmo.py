from datetime import datetime, timedelta
import dateutil.parser
import math
import time
import requests
import json
import pytz
import hmac
import hashlib
import websocket
import logging

from app.models.candle import create_initial_candle_with_duration

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

class Margin(object):
    def __init__(self, available):
        self.available = int(available)

class Ticker(object):
    def __init__(self, product_code, timestamp, bid, ask, volume):
        self.product_code = product_code
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask
        self.volume = volume

    @property
    def mid_price(self):
        return (self.bid + self.ask) / 2

    @property
    def time(self):
        return datetime.utcfromtimestamp(self.timestamp)

    def truncate_date_time(self, duration):
        ticker_time = self.time
        if duration == constants.DURATION_10S:
            ten_sec = math.floor(self.time.second / 10) * 10
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, self.time.minute, ten_sec)
            time_format = '%Y-%m-%d %H:%M:%S'

        elif duration == constants.DURATION_1M:
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_3M:
            three_minute = math.floor(self.time.minute / 3) * 3
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, three_minute)
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_5M:
            five_minute = math.floor(self.time.minute / 5) * 5
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, five_minute)
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_10M:
            ten_minute = math.floor(self.time.minute / 10) * 10
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, ten_minute)
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_15M:
            fifteen_minute = math.floor(self.time.minute / 15) * 15
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, fifteen_minute)
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_30M:
            fifteen_minute = math.floor(self.time.minute / 30) * 30
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, fifteen_minute)
            time_format = '%Y-%m-%d %H:%M'

        elif duration == constants.DURATION_1H:
            time_format = '%Y-%m-%d %H'
        else:
            logger.warning('action=truncate_date_time error=no_datetime_format')
            return None

        str_date = datetime.strftime(ticker_time, time_format)
        return datetime.strptime(str_date, time_format)
    

class Order(object):
    def __init__(self, product_code, side, size, price='',
                 execution_type='MARKET', settle_type=None, order_id=None):
        self.product_code = product_code
        self.side = side
        self.size = size
        self.price = price
        self.execution_type = execution_type
        self.order_id = order_id
        self.settle_type = settle_type

class OrderTimeoutError(Exception):
    """Order timeout error"""

# class Position(object):
#     def __init__(self, product_code, side, size, price='', execution_type=None, position_id=None):
#         self.product_code = product_code
#         self.side = side
#         self.size = size
#         self.price = price
#         self.execution_type = execution_type
#         self.position_id = position_id

class APIClient(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.product_code = settings.product_code
        self.fx_actual_leverage = settings.fx_actual_leverage
        self.public_end_point = settings.gmo_public_end_point
        self.private_end_point = settings.gmo_private_end_point
        self.trade_duration = settings.trade_duration
        # path
        self.send_order_path = settings.gmo_send_order_path
        self.send_close_order_path = settings.gmo_send_close_order_path
        self.send_bulk_close_order_path = settings.gmo_send_bulk_close_order_path
        self.get_margin_path = settings.gmo_get_margin_path
        self.get_ticker_path = settings.gmo_get_ticker_path
        self.get_order_path = settings.gmo_get_order_path
        self.get_executions_path = settings.gmo_get_executions_path
        self.get_open_positions_path = settings.gmo_get_open_positions_path

    def set_initial_candles(self):
        logger.info('action=set_initial_candles status=start')
        for duration in constants.DURATIONS:
            if not (duration == settings.trade_duration):
                continue
            duration_time = constants.TRADE_MAP[duration]['duration']
            if duration_time in constants.GMO_ENABLE_PERIOD:
                candles = self.get_initial_candles()
                create_initial_candle_with_duration(self.product_code, duration, candles)
        logger.info('action=set_initial_candles status=end')

    def get_initial_candles(self):
        try:
            candles = []
            # The GMO's candles period are from 6AM to 6PM
            now = datetime.now(pytz.timezone('Asia/Tokyo')) - timedelta(hours=6)
            if self.trade_duration[-1] == 'm':
                duration = self.trade_duration.replace('m', 'min')

            if self.trade_duration[-1] == 'h':
                duration = self.trade_duration.replace('h', 'hour')

            # get data for the last 10 days
            for num in range(45):
                target_date = (now - timedelta(days=num)).strftime("%Y%m%d")
                path = settings.gmo_kline_path.format(currency=self.product_code,
                                                    duration=duration, 
                                                    date=target_date)
                response = requests.get(self.public_end_point + path)
                candles.extend(response.json()['data'])

            sorted_candles = sorted(candles, key=lambda x: x['openTime'])
            sorted_candles = sorted_candles[-settings.initial_period:]
            list_candles = list(map(lambda x:[int(x["openTime"])/1000, x["open"], x["high"], x["low"], x["close"], x["volume"]], sorted_candles))
            logger.info('action=get_initial_candles status=end')
        except Exception as e:
            logger.error(f'action=get_balance error={e}')
            raise
        return list_candles

    def get_margin(self) -> Margin:
        try:
            method = 'GET'
            end_point = self.private_end_point
            path = self.get_margin_path
            headers = self.make_headers(method, path)
            resp = requests.get(end_point + path, headers=headers)
        except Exception as e:
            logger.error(f'action=get_balance error={e}')
            raise

        available = resp.json()['data']['availableAmount']
        return Margin(available)

    def get_ticker(self, product_code) -> Ticker:
        try:
            method = 'GET'
            end_point = self.public_end_point
            path = self.get_ticker_path.format(product_code=self.product_code)
            headers = self.make_headers(method, path)
            resp = requests.get(end_point + path, headers=headers)
        except Exception as e:
            logger.error(f'action=get_ticker error={e}')
            raise
        resp = resp.json()['data'][0]
        timestamp = datetime.timestamp(dateutil.parser.parse(resp['timestamp']))
        product_code = resp['symbol']
        bid = float(resp['bid'])
        ask = float(resp['ask'])
        volume = float(resp['volume'])
        return Ticker(product_code, timestamp, bid, ask, volume)

    def send_order(self, order: Order):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_order_path

        request_body = {
            'symbol': order.product_code,
            'side': order.side,
            'executionType': order.execution_type,
            'size': order.size,
        }
        logger.info(f'action=send_order status=run time={datetime.now()}')

        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_order error={e}')
            raise
        
        logger.info(f'action=send_order resp={resp.json()}')

        time.sleep(2)
        order_id = resp.json()['data']
        logger.info(f'action=send_order order_id={order_id}')

        order = self.get_order(order_id)
        logger.info(f'action=send_order status=end time={datetime.now()}')
        if not order:
            logger.error('action=send_order error=timeout')
            raise OrderTimeoutError
        
        return order

    # def send_close_order(self, position: Position):
    #     method = 'POST'
    #     end_point = self.private_end_point
    #     path = self.send_close_order_path

    #     if position.side == constants.BUY:
    #         side = 'SELL'
    #     if position.side == constants.SELL:
    #         side = 'BUY'

    #     request_body = {
    #         'symbol': position.product_code,
    #         'side': side,
    #         'executionType': position.execution_type,
    #         'size': position.size,
    #         # "timeInForce": "FAK",
    #         'settlePosition': [
    #             {
    #                 'positionId': position.position_id,
    #                 'size': position.size
    #             }
    #         ]
    #     }
    #     logger.info(f'action=send_close_order status=run time={datetime.now()}')
    #     headers = self.make_headers(method, path, request_body)
    #     try:
    #         resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
    #     except Exception as e:
    #         logger.error(f'action=send_close_order error={e}')
    #         raise
    #     time.sleep(1)
    #     order_id = resp.json()['data']
    #     order = self.get_order(order_id)
    #     logger.info(f'action=send_close_order status=end time={datetime.now()}')
    #     if not order:
    #         logger.error('action=send_close_order error=timeout')
    #         raise OrderTimeoutError
        
    #     return order

    def send_bulk_close_order(self, last_event):
        method = 'POST'
        end_point = self.private_end_point
        path = self.send_bulk_close_order_path

        if last_event.side == constants.BUY:
            side = 'SELL'
        if last_event.side == constants.SELL:
            side = 'BUY'

        request_body = {
            'symbol': last_event.product_code,
            'side': side,
            'executionType': 'MARKET',
            'size': last_event.size
        }
        logger.info(f'action=send_bulk_close_order status=run time={datetime.now()}')
        headers = self.make_headers(method, path, request_body)
        try:
            resp = requests.post(end_point + path, headers=headers, data=json.dumps(request_body))
        except Exception as e:
            logger.error(f'action=send_bulk_close_order error={e}')
            raise
            
        time.sleep(2)
        order_id = resp.json()['data']
        order = self.get_order(order_id)
        logger.info(f'action=send_bulk_close_order status=end time={datetime.now()}')
        if not order:
            logger.error('action=send_bulk_close_order error=timeout')
            raise OrderTimeoutError
        
        return order

    # def wait_order_complete(self, order_id) -> Order:
    #     self.get_order(order_id)

    def get_order(self, order_id) -> Order:
        logger.info(f'action=get_order status=run product_code={self.product_code} order_id={order_id}')
        method = 'GET'
        end_point = self.private_end_point
        path = self.get_order_path
        parameters = { "orderId": order_id }

        headers = self.make_headers(method, path)
        try:
            resp = requests.get(end_point + path, headers=headers, params=parameters)
            logger.info(f'action=get_order resp={resp.json()}')
            resp = resp.json()['data']['list'][0]

        except Exception as e:
            logger.error(f'action=get_order error={e}')
            raise

        if not resp:
            return resp

        order = Order(
            product_code=resp['symbol'],
            side=resp['side'],
            size=float(resp['size']),
            price=float(resp['price']),
            execution_type=resp['executionType'],
            settle_type=resp['settleType'],
            order_id=resp['orderId']
        )
        return order

    def get_executions(self, order_id) -> Order:
        logger.info(f'action=get_executions status=run product_code={self.product_code} order_id={order_id}')
        method = 'GET'
        end_point = self.private_end_point
        path = self.get_executions_path

        parameters = { "orderId": order_id }
        headers = self.make_headers(method, path)
        try:
            resp = requests.get(end_point + path, headers=headers, params=parameters)
            logger.info(f'action=get_executions resp={resp.json()}')
            resp = resp.json()['data']['list'][0]

        except Exception as e:
            logger.error(f'action=get_executions error={e}')
            raise

        if not resp:
            return resp

        order = Order(
            product_code=resp['symbol'],
            side=resp['side'],
            size=float(resp['size']),
            price=float(resp['price']),
            settle_type=resp['settleType'],
            order_id=resp['orderId']
        )
        return order

    # def get_open_positions(self, order_id) -> Order:
    #     logger.info(f'action=get_open_positions status=run product_code={self.product_code}')
    #     method = 'GET'
    #     end_point = self.private_end_point
    #     path = self.get_open_positions_path
    #     parameters = { "symbol": self.product_code }
    #     headers = self.make_headers(method, path)
    #     try:
    #         resp = requests.get(end_point + path, headers=headers, params=parameters)
    #         logger.info(f'action=get_open_positions resp={resp}')

    #     except Exception as e:
    #         logger.error(f'action=get_open_positions error={e}')
    #         raise

    #     if not resp:
    #         return resp

    #     resp = resp.json()['data']['list'][0]
    #     position = Position(
    #         product_code=resp['symbol'],
    #         side=resp['side'],
    #         size=float(resp['size']),
    #         price=float(resp['price']),
    #         position_id=resp['positionId'],
    #     )
    #     return position

    def make_headers(self, method, path, request_body=None):
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        if request_body:
            text = timestamp + method + path + json.dumps(request_body)
        else:
            text = timestamp + method + path
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            'API-KEY': self.api_key,
            'API-TIMESTAMP': timestamp,
            'API-SIGN': sign
        }
        return headers

    def get_size(self, use_percent, decimal_point):
        margin = self.get_margin()
        available = float(margin.available * use_percent)
        ticker = self.get_ticker(self.product_code)
        ask = ticker.ask
        size = available / ask * self.fx_actual_leverage
        size = math.floor(size * 10 ** decimal_point) / (10 ** decimal_point)
        return size

class RealtimeAPI(object):

    def __init__(self, url, channel, callback):
        self.url = url
        self.channel = channel
        self.callback = callback
        self.product_code = settings.product_code
        self.connect()

    def connect(self):
        self.ws = websocket.WebSocketApp(self.url,header=None,on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.run_forever()
        logger.info('Web Socket process ended.')
        
    """
    Below are callback functions of websocket.
    """
    # when we get message
    def on_message(self, ws, message):
        resp = json.loads(message)
        self.set_realtime_ticker(resp, self.callback)

    # when error occurs
    def on_error(self, ws, error, _="", __ =""):
        logger.error(error)
        if error:
            time.sleep(5)
            self.connect()

    # when websocket closed.
    def on_close(self, ws):
        logger.info('disconnected streaming server')

    # when websocket opened.
    def on_open(self, ws):
        logger.info('connected streaming server')
        input_data = json.dumps(
            {'command' : 'subscribe',
            'channel' : self.channel,
            'symbol' : self.product_code,
            }
        )
        ws.send(input_data)
        
    def set_realtime_ticker(self, resp, callback):
        timestamp = datetime.timestamp(
            dateutil.parser.parse(resp['timestamp']))
        product_code = resp['symbol']
        bid = float(resp['bid'])
        ask = float(resp['ask'])
        volume = float(resp['volume'])
        ticker = Ticker(product_code, timestamp, bid, ask, volume)
        callback(ticker)

class Common(object):
    def __init__(self, product_code, side, size, price='', execution_type=None, position_id=None):
        self.product_code = product_code
        self.side = side
        self.size = size
        self.price = price
        self.execution_type = execution_type
        self.position_id = position_id