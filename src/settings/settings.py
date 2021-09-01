import configparser

from utils.utils import bool_from_str

conf = configparser.ConfigParser()
conf.read('settings/settings.ini')

bitflyer_api_key = conf['bitflyer']['api_key']
bitflyer_api_secret = conf['bitflyer']['api_secret']
bitflyer_realtime_api_end_point = conf['bitflyer']['realtime_api_end_point']
bitflyer_realtime_ticker_product_code = conf['bitflyer']['realtime_ticker_product_code']
bitflyer_commission_percentage = float(conf['bitflyer']['commission_percentage'])
bitflyer_maintenance_start_time = conf['bitflyer']['maintenance_start_time']
bitflyer_maintenance_end_time = conf['bitflyer']['maintenance_end_time']

bitflyer_btcjpy_ohlc_url = conf['cryptowatch']['bitflyer_btcjpy_ohlc_url']

gmo_api_key = conf['gmo']['api_key']
gmo_api_secret = conf['gmo']['api_secret']
gmo_public_end_point = conf['gmo']['public_end_point']
gmo_private_end_point = conf['gmo']['private_end_point']
gmo_kline_path = conf['gmo']['kline_path']
gmo_send_order_path = conf['gmo']['send_order_path']
gmo_send_close_order_path = conf['gmo']['send_close_order_path']
gmo_get_margin_path = conf['gmo']['get_margin_path']
gmo_get_ticker_path = conf['gmo']['get_ticker_path']
gmo_get_order_path = conf['gmo']['get_order_path']
gmo_get_executions_path = conf['gmo']['get_executions_path']
gmo_get_open_positions_path = conf['gmo']['get_open_positions_path']
gmo_realtime_api_end_point = conf['gmo']['realtime_api_end_point']

fx_leverage = float(conf['fx']['leverage'])
fx_actual_leverage = float(conf['fx']['actual_leverage'])

product_code = conf['currency']['product_code']
buy_currency = conf['currency']['buy_currency']
sell_currency = conf['currency']['sell_currency']

db_name = conf['db']['name']
db_driver = conf['db']['driver']

environment = conf['trading']['environment']
trade_duration = conf['trading']['trade_duration'].lower()
use_percent = float(conf['trading']['use_percent'])
initial_period = int(conf['trading']['initial_period'])
past_period = int(conf['trading']['past_period'])
minimum_period = int(conf['trading']['minimum_period'])
storage_period = int(conf['trading']['storage_period'])
stop_limit_percent = float(conf['trading']['stop_limit_percent'])
num_ranking = int(conf['trading']['num_ranking'])
get_ticker_duration = int(conf['trading']['get_ticker_duration'])
execute_delete_candle_duration = int(conf['trading']['execute_delete_candle_duration'])