DURATION_1M = '1m'
DURATION_1H = '1h'
DURATIONS = [DURATION_1M, DURATION_1H]

GRANULARITY_1M = 'M1'
GRANULARITY_1H = 'H1'

TRADE_MAP = {
    DURATION_1M: {
        'duration': DURATION_1M,
        'granularity': GRANULARITY_1M,
    },
    DURATION_1H: {
        'duration': DURATION_1H,
        'granularity': GRANULARITY_1H,
    }
}

BUY = "BUY"
SELL = "SELL"
PRODUCT_CODE_BTC_JPY = "BTC_JPY"