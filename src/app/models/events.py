import datetime
import logging

import omitempty
from sqlalchemy import Column
from sqlalchemy import desc
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from app.models.base import session_scope
from app.models.base import Base

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)

class SignalEvent(Base):
    __tablename__ = 'signal_event'

    time = Column(DateTime, primary_key=True, nullable=False)
    product_code = Column(String)
    side = Column(String)
    price = Column(Float)
    size = Column(Float)
    order_id = Column(Integer)
    settle_type = Column(String)
    indicator = Column(String)

    def save(self):
        with session_scope() as session:
            session.add(self)

    @property
    def value(self):
        dict_values = omitempty({
            'time': self.time,
            'product_code': self.product_code,
            'side': self.side,
            'price': self.price,
            'size': self.size,
            'order_id': self.order_id,
            'settle_type': self.settle_type,
            'indicator': self.indicator,
        })
        if not dict_values:
            return None
        return dict_values

    @classmethod
    def get_signal_events_by_count(cls, count, prduct_code=settings.product_code):
        with session_scope() as session:
            rows = session.query(cls).filter(cls.product_code == prduct_code).order_by(desc(cls.time)).limit(count).all()
            if rows is None:
                return []
            rows.reverse()
            return rows

    @classmethod
    def get_signal_events_after_time(cls, time):
        with session_scope() as session:
            rows = session.query(cls).filter(cls.time >= time).all()

            if rows is None:
                return []

            return rows

class SignalEvents(object):
    def __init__(self, signals=None):
        if signals is None:
            self.signals = []
        else:
            self.signals = signals

    def can_buy(self, time):
        if len(self.signals) == 0:
            return True

        last_signal = self.signals[-1]
        if last_signal.side == constants.SELL and last_signal.time < time:
            return True

        return False

    def can_sell(self, time):
        if len(self.signals) == 0:
            return False

        last_signal = self.signals[-1]
        if last_signal.side == constants.BUY and last_signal.time < time:
            return True

        return False

    def can_buy_fx(self, time):
        if len(self.signals) == 0:
            return True

        last_signal = self.signals[-1]
        if last_signal.side == constants.SELL and last_signal.time < time:
            return True

        if last_signal.side == constants.BUY and last_signal.settle_type == constants.CLOSE and last_signal.time <= time:
            return True

        return False

    def can_sell_fx(self, time):
        if len(self.signals) == 0:
            return True

        last_signal = self.signals[-1]
        if last_signal.side == constants.BUY and last_signal.time < time:
            return True

        if last_signal.side == constants.SELL and last_signal.settle_type == constants.CLOSE and last_signal.time <= time:
            return True

        return False

    def get_next_order_settle_type(self):
        if settings.trade_type != constants.TRADE_TYPE_FX:
            return ''
            
        if len(self.signals) == 0:
            return constants.OPEN

        last_signal = self.signals[-1]
        if last_signal.settle_type == constants.OPEN:
            return constants.CLOSE

        if last_signal.settle_type == constants.CLOSE:
            return constants.OPEN

    def buy(self, product_code, time, price, size, order_id=None, settle_type=None, indicator=None, save=True):

        if settings.trade_type == constants.TRADE_TYPE_BUY:
            if not self.can_buy(time):
                return False

        if settings.trade_type == constants.TRADE_TYPE_FX:
            if not self.can_buy_fx(time):
                return False

        signal_event = SignalEvent(time=time, 
                                   product_code=product_code, 
                                   side=constants.BUY, 
                                   price=price, 
                                   size=size,
                                   order_id=order_id,
                                   settle_type=settle_type,
                                   indicator=indicator)
        if save:
            signal_event.save()

        self.signals.append(signal_event)

        return True

    def sell(self, product_code, time, price, size, order_id=None, settle_type=None, indicator=None, save=True):

        if settings.trade_type == constants.TRADE_TYPE_BUY:
            if not self.can_sell(time):
                return False

        if settings.trade_type == constants.TRADE_TYPE_FX:
            if not self.can_sell_fx(time):
                return False

        signal_event = SignalEvent(time=time,
                                   product_code=product_code,
                                   side=constants.SELL,
                                   price=price,
                                   size=size,
                                   order_id=order_id,
                                   settle_type=settle_type,
                                   indicator=indicator)
        if save:
            signal_event.save()

        self.signals.append(signal_event)

        return True

    @staticmethod
    def get_signal_events_by_count(count:int):
        signal_events = SignalEvent.get_signal_events_by_count(count)
        return SignalEvents(signal_events)

    @staticmethod
    def get_signal_events_after_time(time: datetime.datetime.time):
        signal_events = SignalEvent.get_signal_events_after_time(time)
        return SignalEvents(signal_events)

    @property
    def profit(self):
        total = 0.0
        before_sell = 0.0
        is_holding = False
        for i in range(len(self.signals)):
            signal_event = self.signals[i]
            if i == 0 and signal_event.side == constants.SELL:
                continue
            if signal_event.side == constants.BUY:
                total -= signal_event.price * signal_event.size
                is_holding = True
            if signal_event.side == constants.SELL:
                total += signal_event.price * signal_event.size
                is_holding = False
                before_sell = total
        if is_holding:
            return before_sell
        return total

    @property
    def profit_fx(self):
        total = 0.0
        before_close = 0.0
        is_holding = False
        for i in range(len(self.signals)):
            signal_event = self.signals[i]
            if signal_event.side == constants.BUY and signal_event.settle_type == constants.OPEN:
                total -= signal_event.price * signal_event.size
                is_holding = True

            if signal_event.side == constants.BUY and signal_event.settle_type == constants.CLOSE:
                total -= signal_event.price * signal_event.size
                is_holding = False
                before_close = total

            if signal_event.side == constants.SELL and signal_event.settle_type == constants.OPEN:
                total += signal_event.price * signal_event.size
                is_holding = True

            if signal_event.side == constants.SELL and signal_event.settle_type == constants.CLOSE:
                total += signal_event.price * signal_event.size
                is_holding = False
                before_close = total
                
        if is_holding:
            return before_close
        return total

    @property
    def value(self):
        signals = [s.value for s in self.signals]
        if not signals:
            signals = None

        if settings.trade_type == constants.TRADE_TYPE_BUY:
            profit = self.profit
            if not self.profit:
                profit = None

        if settings.trade_type == constants.TRADE_TYPE_FX:
            profit = self.profit_fx
            if not self.profit_fx:
                profit = None

        return {
            'signals': signals,
            'profit': profit
        }