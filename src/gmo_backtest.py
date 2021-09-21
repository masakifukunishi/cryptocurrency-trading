{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6c2deda2-5462-4b85-88a9-cc329735c130",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "import logging\n",
    "\n",
    "format = \"%(asctime)s %(levelname)s %(name)s :%(message)s\"\n",
    "logging.basicConfig(filename=\"console.log\",level=logging.INFO, format=format)\n",
    "\n",
    "from app.models.candle import create_backtest_candle_with_duration\n",
    "from app.controllers.gmo.ai import AI\n",
    "from gmo.gmo import APIClient\n",
    "\n",
    "import settings.constants as constants\n",
    "import settings.settings as settings\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    ai = AI()\n",
    "    API = APIClient(settings.gmo_api_key, settings.gmo_api_secret)\n",
    "    duration_time = constants.TRADE_MAP[settings.trade_duration]['duration']\n",
    "    if duration_time in constants.GMO_ENABLE_PERIOD:\n",
    "        candles = API.get_initial_candles(settings.backtest_period)\n",
    "        for candle in candles:\n",
    "            create_backtest_candle_with_duration(settings.product_code, settings.trade_duration, candle)\n",
    "            ai.trade(is_created=True)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
