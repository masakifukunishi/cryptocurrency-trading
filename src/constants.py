DURATION_10S = '10s'
DURATION_1M = '1m'
DURATION_1H = '1h'
DURATIONS = [DURATION_10S, DURATION_1M, DURATION_1H]
GRANULARITY_10S = '10'
GRANULARITY_1M = '60'
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
    DURATION_1H: {
        'duration': DURATION_1H,
        'granularity': GRANULARITY_1H,
    },
}

BUY = "BUY"
SELL = "SELL"
PRODUCT_CODE_BTC_JPY = "BTC_JPY"

ENVIRONMENT_DEV = "dev"
ENVIRONMENT_STAGING = "staging"
ENVIRONMENT_PRODUCTION = "production"