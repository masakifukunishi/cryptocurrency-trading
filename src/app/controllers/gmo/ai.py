import datetime
import logging
import time
import math

import numpy as np
import talib

from app.models.candle import factory_candle_class
from app.models.dfcandle import DataFrameCandle
from app.models.events import SignalEvents
from gmo.gmo import APIClient
from gmo.gmo import Order
from tradingalgo.algo import ichimoku_cloud

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)


def duration_seconds(duration: str) -> int:
    if duration == constants.DURATION_10S:
        return 10
    if duration == constants.DURATION_1M:
        return 60
    if duration == constants.DURATION_3M:
        return 60 * 3
    if duration == constants.DURATION_5M:
        return 60 * 5
    if duration == constants.DURATION_15M:
        return 60 * 15
    if duration == constants.DURATION_30M:
        return 60 * 30
    if duration == constants.DURATION_1H:
        return 60 * 60
    else:
        return 0


class AI(object):

    def __init__(self, product_code, use_percent, duration, past_period, stop_limit_percent_sell, stop_limit_percent_buy, environment, fx_leverage, fx_actual_leverage):
        self.API = APIClient(settings.gmo_api_key, settings.gmo_api_secret)
        self.API.set_initial_candles()

        self.signal_events = SignalEvents.get_signal_events_by_count(1)
        self.product_code = product_code
        self.use_percent = use_percent
        self.duration = duration
        self.past_period = past_period
        self.optimized_trade_params = None
        self.stop_limit_buy = 0
        self.stop_limit_sell = 0
        self.stop_limit_percent_sell = stop_limit_percent_sell
        self.stop_limit_percent_buy = stop_limit_percent_buy
        self.environment = environment
        self.fx_leverage = fx_leverage
        self.fx_actual_leverage = fx_actual_leverage
        self.start_trade = datetime.datetime.utcnow()
        self.candle_cls = factory_candle_class(self.product_code, self.duration)
        self.update_optimize_params(False)
        self.decimal_point = 2

    def update_optimize_params(self, is_continue: bool):
        logger.info(f'action=update_optimize_params status=run is_continue={is_continue}')
        df = DataFrameCandle(self.product_code, self.duration)
        df.set_all_candles(self.past_period)
        if df.candles:
            self.optimized_trade_params = df.optimize_params()
        if self.optimized_trade_params is not None:
            logger.info(f'action=update_optimize_params params={self.optimized_trade_params.__dict__}')

        logger.info(f'action=update_optimize_params status=end')
        
        if is_continue and self.optimized_trade_params is None:
            time.sleep(10 * duration_seconds(self.duration))
            self.update_optimize_params(is_continue)

    def buy(self, candle, indicator):
        next_order_settle_type = self.signal_events.get_next_order_settle_type()
        if not self.signal_events.can_buy_fx(candle.time):
            return False
            
        if self.environment == constants.ENVIRONMENT_DEV:
            could_buy = self.signal_events.buy(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = 0.1,
                                               settle_type = next_order_settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_buy

        if self.start_trade > candle.time:
            return False
            
        # staging
        if self.environment == constants.ENVIRONMENT_STAGING:
            could_buy = self.signal_events.buy(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = 0.1,
                                               settle_type = next_order_settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_buy

        # production
        if self.environment == constants.ENVIRONMENT_PRODUCTION:
            if next_order_settle_type == constants.OPEN:
                size = self.API.get_size(self.use_percent, self.decimal_point)
                order = Order(self.product_code, constants.BUY, size)
                resp = self.API.send_order(order)

            if next_order_settle_type == constants.CLOSE:
                last_event = self.signal_events.signals[-1]
                resp = self.API.send_bulk_close_order(last_event)

            if not resp:
                logger.error(f'action=buy status=error responce={resp}')
                return False
            logger.info(f'action=buy responce={resp}')
            could_buy = self.signal_events.buy(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = resp.size,
                                               order_id = resp.order_id,
                                               settle_type = resp.settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_buy

    def sell(self, candle, indicator):
        if not self.signal_events.can_sell_fx(candle.time):
            return False
        next_order_settle_type = self.signal_events.get_next_order_settle_type()
        # dev
        if self.environment == constants.ENVIRONMENT_DEV:
            could_sell = self.signal_events.sell(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = 0.1,
                                               settle_type = next_order_settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_sell

        if self.start_trade > candle.time:
            return False

        # staging
        if self.environment == constants.ENVIRONMENT_STAGING:
            could_sell = self.signal_events.sell(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = 0.1,
                                               settle_type = next_order_settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_sell

        # production
        if self.environment == constants.ENVIRONMENT_PRODUCTION:
            if next_order_settle_type == constants.OPEN:
                size = self.API.get_size(self.use_percent, self.decimal_point)
                order = Order(self.product_code, constants.SELL, size)
                resp = self.API.send_order(order)

            if next_order_settle_type == constants.CLOSE:
                last_event = self.signal_events.signals[-1]
                resp = self.API.send_bulk_close_order(last_event)
            
            if not resp:
                logger.error(f'action=buy status=error responce={resp}')
                return False
            logger.info(f'action=sell responce={resp}')
            could_sell = self.signal_events.sell(product_code = self.product_code,
                                               time = candle.time,
                                               price = candle.close,
                                               size = resp.size,
                                               order_id = resp.order_id,
                                               settle_type = resp.settle_type,
                                               indicator = indicator,
                                               save=True)
            return could_sell

    def trade(self):
        logger.info('action=trade status=run')
        df = DataFrameCandle(self.product_code, self.duration)
        df.set_all_candles(self.past_period)
        params = self.optimized_trade_params
        
        if params is None:
            logger.info(f'action=trade optimized_trade_params=None candles={len(df.candles)}')
            if len(df.candles) >= settings.minimum_period:
                self.start_trade = datetime.datetime.utcnow()
                self.update_optimize_params(is_continue=False)
            return

        if params.ema_enable:
            ema_values_1 = talib.EMA(np.array(df.closes), params.ema_period_1)
            ema_values_2 = talib.EMA(np.array(df.closes), params.ema_period_2)

        if params.bb_enable:
            bb_up, _, bb_down = talib.BBANDS(np.array(df.closes), params.bb_n, params.bb_k, params.bb_k, 0)

        if params.ichimoku_enable:
            tenkan, kijun, senkou_a, senkou_b, chikou = ichimoku_cloud(df.closes)

        if params.rsi_enable:
            rsi_values = talib.RSI(np.array(df.closes), params.rsi_period)

        if params.macd_enable:
            macd, macd_signal, _ = talib.MACD(np.array(df.closes), params.macd_fast_period, params.macd_slow_period, params.macd_signal_period)

        for i in range(1, len(df.candles)):
            buy_point, sell_point = 0, 0
            trade_log = ''
            if params.ema_enable and params.ema_period_1 <= i and params.ema_period_2 <= i:
                if ema_values_1[i - 1] < ema_values_2[i - 1] and ema_values_1[i] >= ema_values_2[i]:
                    buy_point += 1
                    trade_log += f'action=trade side=buy indicator=ema period_1={params.ema_period_1} period_2={params.ema_period_2}\n'

                if ema_values_1[i - 1] > ema_values_2[i - 1] and ema_values_1[i] <= ema_values_2[i]:
                    sell_point += 1
                    trade_log += f'action=trade side=sell indicator=ema period_1={params.ema_period_1} period_2={params.ema_period_2}\n'

            if params.bb_enable and params.bb_n <= i:
                if bb_down[i - 1] > df.candles[i - 1].close and bb_down[i] <= df.candles[i].close:
                    buy_point += 1
                    trade_log += f'action=trade side=buy indicator=bb n={params.bb_n} k={params.bb_k}\n'

                if bb_up[i - 1] < df.candles[i - 1].close and bb_up[i] >= df.candles[i].close:
                    sell_point += 1
                    trade_log += f'action=trade side=sell indicator=bb n={params.bb_n} k={params.bb_k}\n'

            if params.ichimoku_enable:
                if (chikou[i-1] < df.candles[i-1].high and
                        chikou[i] >= df.candles[i].high and
                        senkou_a[i] < df.candles[i].low and
                        senkou_b[i] < df.candles[i].low and
                        tenkan[i] > kijun[i]):
                    buy_point += 1
                    trade_log += 'action=trade side=buy indicator=ichimoku\n'

                if (chikou[i - 1] > df.candles[i - 1].low and
                        chikou[i] <= df.candles[i].low and
                        senkou_a[i] > df.candles[i].high and
                        senkou_b[i] > df.candles[i].high and
                        tenkan[i] < kijun[i]):
                    sell_point += 1
                    trade_log += 'action=trade side=sell indicator=ichimoku\n'

            if params.rsi_enable and rsi_values[i-1] != 0 and rsi_values[i-1] != 100:
                if rsi_values[i-1] < params.rsi_buy_thread and rsi_values[i] >= params.rsi_buy_thread:
                    buy_point += 1
                    trade_log += f'action=trade side=buy indicator=rsi period={params.rsi_period} buy_thread={params.rsi_buy_thread}\n'

                if rsi_values[i-1] > params.rsi_sell_thread and rsi_values[i] <= params.rsi_sell_thread:
                    sell_point += 1
                    trade_log += f'action=trade side=sell indicator=rsi period={params.rsi_period} sell_thread={params.rsi_sell_thread}\n'

            if params.macd_enable:
                if macd[i] < 0 and macd_signal[i] < 0 and macd[i - 1] < macd_signal[i - 1] and macd[i] >= macd_signal[i]:
                    buy_point += 1
                    trade_log += f'action=trade side=buy indicator=macd fast_period={params.macd_fast_period} slow_period={params.macd_slow_period} signal_period={params.macd_signal_period}\n'

                if macd[i] > 0 and macd_signal[i] > 0 and macd[i-1] > macd_signal[i - 1] and macd[i] <= macd_signal[i]:
                    sell_point += 1
                    trade_log += f'action=trade side=sell indicator=macd fast_period={params.macd_fast_period} slow_period={params.macd_slow_period} signal_period={params.macd_signal_period}\n'

            if buy_point > 0:
                indicator = trade_log.rstrip('\n')
                if not self.buy(df.candles[i], indicator):
                    continue

                logger.info(trade_log.rstrip('\n'))
                logger.info(f'action=buy buy_point={buy_point} environment={self.environment} status=completion')

                last_event = self.signal_events.signals[-1]
                if last_event.settle_type == constants.OPEN:
                    self.stop_limit_sell = df.candles[i].close * self.stop_limit_percent_sell
                if last_event.settle_type == constants.CLOSE:
                    self.stop_limit_buy = 0.0
                    self.update_optimize_params(is_continue=True)

            if sell_point > 0 or self.stop_limit_sell > df.candles[i].close:
                indicator = trade_log.rstrip('\n')
                if not self.sell(df.candles[i], indicator):
                    continue

                logger.info(trade_log.rstrip('\n'))
                logger.info(f'action=sell sell_point={sell_point} environment={self.environment} status=completion')

                last_event = self.signal_events.signals[-1]
                if last_event.settle_type == constants.OPEN:
                    self.stop_limit_buy = df.candles[i].close * self.stop_limit_percent_buy
                if last_event.settle_type == constants.CLOSE:
                    self.stop_limit_sell = 0.0
                    self.update_optimize_params(is_continue=True)
                