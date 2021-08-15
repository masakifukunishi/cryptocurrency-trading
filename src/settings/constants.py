DURATION_10S = '10s'
DURATION_1M = '1m'
DURATION_3M = '3m'
DURATION_5M = '5m'
DURATION_15M = '15m'
DURATION_1H = '1h'
# DURATIONS = [DURATION_10S, DURATION_1M, DURATION_3M, DURATION_5M, DURATION_15M, DURATION_1H]
DURATIONS = [DURATION_1M]
GRANULARITY_10S = '10'
GRANULARITY_1M = '60'
GRANULARITY_3M = '180'
GRANULARITY_5M = '300'
GRANULARITY_15M = '900'
GRANULARITY_1H = '3600'



TRADE_MAP = {
    DURATION_10S: {
        'duration': DURATION_10S,
        'granularity': GRANULARITY_10S,
    },
    DURATION_1M: {
        'duration': DURATION_1M,
        'granularity': GRANULARITY_1M,
    },
    DURATION_3M: {
        'duration': DURATION_3M,
        'granularity': GRANULARITY_3M,
    },
    DURATION_5M: {
        'duration': DURATION_5M,
        'granularity': GRANULARITY_5M,
    },
    DURATION_15M: {
        'duration': DURATION_15M,
        'granularity': GRANULARITY_15M,
    },
    DURATION_1H: {
        'duration': DURATION_1H,
        'granularity': GRANULARITY_1H,
    },
}

BUY = 'BUY'
SELL = 'SELL'
PRODUCT_CODE_BTC_JPY = 'BTC_JPY'

ENVIRONMENT_DEV = 'dev'
ENVIRONMENT_STAGING = 'staging'
ENVIRONMENT_PRODUCTION = 'production'

# 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 3d, 1w
CRYPTOWATCH_ENABLE_PERIOD = ['60', '180', '300', '900', '1800', '3600', '7200', '14400', '21600', '43200', '86400', '259200', '604800']