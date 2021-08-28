from datetime import datetime
import logging
import time

from sqlalchemy import Column
from sqlalchemy import desc
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.exc import IntegrityError

from app.models.base import Base
from app.models.base import session_scope

import settings.constants as constants
import settings.settings as settings

logger = logging.getLogger(__name__)
        
class BaseCandleMixin(object):
    time = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)

    @classmethod
    def create(cls, time, open, close, high, low, volume):
        candle = cls(time=time,
                     open=open,
                     close=close,
                     high=high,
                     low=low,
                     volume=volume)
        try:
            with session_scope() as session:
                session.add(candle)
            return candle
        except IntegrityError:
            return False

    @classmethod
    def delete(cls, times):
        with session_scope() as session:
             session.query(cls).filter(cls.time.not_in(times)).delete()
            
    @classmethod
    def is_exists_cnadle(cls):
        with session_scope() as session:
            candle = session.query(cls).first()
        if candle is None:
            return False
        return True
    
    @classmethod
    def get(cls, time):
        with session_scope() as session:
            candle = session.query(cls).filter(
                cls.time == time).first()
        if candle is None:
            return None
        return candle
    
    def save(self):
        with session_scope() as session:
            session.add(self)

    @classmethod
    def get_all_candles(cls, limit=100):
        with session_scope() as session:
            candles = session.query(cls).order_by(
                desc(cls.time)).limit(limit).all()

        if candles is None:
            return None

        candles.reverse()
        return candles

    @property
    def value(self):
        return {
            'time': self.time,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
        }
    
class BtcJpyBaseCandle10S(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_10S'
    
class BtcJpyBaseCandle1M(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_1M'

class BtcJpyBaseCandle3M(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_3M'

class BtcJpyBaseCandle5M(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_5M'

class BtcJpyBaseCandle15M(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_15M'

class BtcJpyBaseCandle1H(BaseCandleMixin, Base):
    __tablename__ = 'BTC_JPY_1H'
    

def factory_candle_class(product_code, duration):
    if product_code == constants.PRODUCT_CODE_BTC_JPY:
        if duration == constants.DURATION_10S:
            return BtcJpyBaseCandle10S
        if duration == constants.DURATION_1M:
            return BtcJpyBaseCandle1M
        if duration == constants.DURATION_3M:
            return BtcJpyBaseCandle3M
        if duration == constants.DURATION_5M:
            return BtcJpyBaseCandle5M
        if duration == constants.DURATION_15M:
            return BtcJpyBaseCandle15M
        if duration == constants.DURATION_1H:
            return BtcJpyBaseCandle1H

def create_candle_with_duration(product_code, duration, ticker):
    cls = factory_candle_class(product_code, duration)
    ticker_time = ticker.truncate_date_time(duration)
    current_candle = cls.get(ticker_time)
    price = ticker.mid_price
    if current_candle is None:
        cls.create(ticker_time, price, price, price, price, ticker.volume)
        return True

    if current_candle.high <= price:
        current_candle.high = price
    elif current_candle.low >= price:
        current_candle.low = price
    current_candle.volume += ticker.volume
    current_candle.close = price
    current_candle.save()
    return False

def create_initial_candle_with_duration(product_code, duration, candles):
    logger.info(f'action=create_initial_candle_with_duration duration={duration} status=run')
    
    cls = factory_candle_class(product_code, duration)
    if cls.is_exists_cnadle():
        logger.warning('candles already exists')
        return False
    
    for candle in candles:
        time = datetime.fromtimestamp(candle[0])
        print(time)
        open = candle[1]
        high = candle[2]
        low = candle[3]
        close = candle[4]
        volume = candle[5]
        cls.create(time, open, close, high, low, volume)
    
    logger.info(f'action=create_initial_candle_with_duration duration={duration} status=completion')
    
    return True

def delete_candle(product_code, duration):
    logger.info(f'action=delete_candle duration={duration} status=run')
    cls = factory_candle_class(product_code, duration)
    candles_cls = cls.get_all_candles(settings.storage_period)
    times = [c.value["time"] for c in candles_cls]
    cls.delete(times)
    logger.info(f'action=delete_candle duration={duration} status=end')