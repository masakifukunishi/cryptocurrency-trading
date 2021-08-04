import configparser

from utils.utils import bool_from_str

conf = configparser.ConfigParser()
conf.read('settings/settings.ini')

api_key = conf['bitflyer']['api_key']
api_secret = conf['bitflyer']['api_secret']
product_code = conf['bitflyer']['product_code']
realtime_api_end_point = conf['bitflyer']['realtime_api_end_point']
realtime_ticker_product_code = conf['bitflyer']['realtime_ticker_product_code']

bitflyer_btcjpy_ohlc_url = conf['cryptowatch']['bitflyer_btcjpy_ohlc_url']

db_name = conf['db']['name']
db_driver = conf['db']['driver']

environment = conf['pytrading']['environment']
trade_duration = conf['pytrading']['trade_duration'].lower()
use_percent = float(conf['pytrading']['use_percent'])
initial_period = int(conf['pytrading']['initial_period'])
past_period = int(conf['pytrading']['past_period'])
minimum_period = int(conf['pytrading']['minimum_period'])
stop_limit_percent = float(conf['pytrading']['stop_limit_percent'])
num_ranking = int(conf['pytrading']['num_ranking'])
get_ticker_duration = int(conf['pytrading']['get_ticker_duration'])