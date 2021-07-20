from datetime import datetime
import logging
import math
import time
import json
import websocket

import dateutil.parser
import pybitflyer

import constants
import settings

logger = logging.getLogger(__name__)

ORDER_COMPLETED = 'COMPLETED'

class Balance(object):
    def __init__(self, currency, available):
        self.currency = currency
        self.available = available

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
            new_sec = math.floor(self.time.second / 10) * 10
            ticker_time = datetime(
                self.time.year, self.time.month, self.time.day,
                self.time.hour, self.time.minute, new_sec)
            time_format = '%Y-%m-%d %H:%M:%S'
        elif duration == constants.DURATION_1M:
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
                 child_order_type='MARKET', minute_to_expire=10, child_order_state=None, child_order_acceptance_id=None):
        self.product_code = product_code
        self.side = side
        self.size = size
        self.price = price
        self.child_order_type = child_order_type
        self.minute_to_expire = minute_to_expire
        self.child_order_state = child_order_state
        self.child_order_acceptance_id = child_order_acceptance_id

class OrderTimeoutError(Exception):
    """Order timeout error"""
    
class APIClient(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = pybitflyer.API(api_key=api_key, api_secret=api_secret)

    def get_balance_jpy(self) -> Balance:
        try:
            resp = self.client.getbalance()
        except Exception as e:
            logger.error(f'action=get_balance_jpy error={e}')
            raise
        currency = resp[0]['currency_code']
        available = resp[0]['available']
        return Balance(currency, available)

    def get_balance_btc(self) -> Balance:
        try:
            resp = self.client.getbalance()
        except Exception as e:
            logger.error(f'action=get_balance_btc error={e}')
            raise
        currency = resp[1]['currency_code']
        available = resp[1]['available']
        return Balance(currency, available)
    

    def get_ticker(self, product_code) -> Ticker:
        try:
            resp = self.client.ticker(product_code=product_code)
        except Exception as e:
            logger.error(f'action=get_ticker error={e}')
            raise
        timestamp = datetime.timestamp(
            dateutil.parser.parse(resp['timestamp']))
        product_code = resp['product_code']
        bid = float(resp['best_bid'])
        ask = float(resp['best_ask'])
        volume = float(resp['volume'])
        return Ticker(product_code, timestamp, bid, ask, volume)

    def get_realtime_ticker(self, product_code, callback):
        while True:
            try:
                resp = self.client.ticker(product_code=product_code)
            except Exception as e:
                logger.error(f'action=get_realtime_ticker error={e}')
                time.sleep(1.5)
                continue
            timestamp = datetime.timestamp(
                dateutil.parser.parse(resp['timestamp']))
            product_code = resp['product_code']
            bid = float(resp['best_bid'])
            ask = float(resp['best_ask'])
            volume = float(resp['volume'])
            ticker = Ticker(product_code, timestamp, bid, ask, volume)
            callback(ticker)
            time.sleep(settings.get_ticker_duration)
            
    def send_order(self, order: Order):
        logger.info(f'action=send_order status=run time={datetime.utcnow()}')
        try:
            resp = self.client.sendchildorder(product_code=order.product_code,
                                     child_order_type=order.child_order_type,
                                     side=order.side,
                                     size=order.size,
                                     minute_to_expire=order.minute_to_expire)
            logger.info(f'action=send_order resp={resp}')
        except Exception as e:
            logger.error(f'action=send_order error={e}')
            raise
        # resp = {'child_order_acceptance_id': 'JRF20210702-105120-972173'}
        time.sleep(1)
        order_id = resp['child_order_acceptance_id']
        order = self.wait_order_complete(order_id)
        logger.info(f'action=send_order status=end time={datetime.utcnow()}')
        if not order:
            logger.error('action=send_order error=timeout')
            raise OrderTimeoutError
        
        return order

    def wait_order_complete(self, order_id) -> Order:
        count = 0
        timeout_count = 5
        while True:
            order = self.get_order(order_id)
            if order.child_order_state == ORDER_COMPLETED:
                return order
            time.sleep(1)
            count += 1
            if count > timeout_count:
                return None

    def get_order(self, order_id) -> Order:
        logger.info(f'action=get_order status=run product_code={settings.product_code} child_order_acceptance_id={order_id}')
        try:
            resp = self.client.getchildorders(product_code=settings.product_code,
                                     child_order_acceptance_id=order_id)
            logger.info(f'action=get_order resp={resp}')
        except Exception as e:
            logger.error(f'action=get_order error={e}')
            raise
        order = Order(
            product_code=resp[0]['product_code'],
            side=resp[0]['side'],
            size=float(resp[0]['size']),
            price=float(resp[0]['average_price']),
            child_order_type=resp[0]['child_order_type'],
            child_order_state=resp[0]['child_order_state'],
            child_order_acceptance_id=resp[0]['child_order_acceptance_id']
        )
        return order

class RealtimeAPI(object):

    def __init__(self, url, channel, callback):
        self.url = url
        self.channel = channel
        self.callback = callback
        self.connect()

    def connect(self):
        self.ws = websocket.WebSocketApp(self.url,header=None,on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.keep_running = True 
        self.ws.run_forever()
        logger.info('Web Socket process ended.')

    def disconnect(self):
        self.ws.keep_running = False
        self.ws.close()
        
    """
    Below are callback functions of websocket.
    """
    # when we get message
    def on_message(self, ws, message):
        resp = json.loads(message)['params']['message']
        self.set_realtime_ticker(resp, self.callback)

    # when error occurs
    def on_error(self, ws, error, _="", __ =""):
        logger.error(error)
        self.disconnect()
        time.sleep(2)
        self.connect()

    # when websocket closed.
    def on_close(self, ws):
        logger.info('disconnected streaming server')

    # when websocket opened.
    def on_open(self, ws):
        logger.info('connected streaming server')
        input_data = json.dumps(
            {'method' : 'subscribe',
            'params' : {'channel' : self.channel}
            }
        )
        ws.send(input_data)
        
    def set_realtime_ticker(self, resp, callback):
        timestamp = datetime.timestamp(
            dateutil.parser.parse(resp['timestamp']))
        product_code = resp['product_code']
        bid = float(resp['best_bid'])
        ask = float(resp['best_ask'])
        volume = float(resp['volume'])
        ticker = Ticker(product_code, timestamp, bid, ask, volume)
        callback(ticker)