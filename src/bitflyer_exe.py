import sys
from threading import Thread
import logging

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)

from app.controllers.initialprocess import InitialProcess
# from app.controllers.dataprocess import DataProcess

if __name__ == "__main__":
    initial = InitialProcess()
    initial.set_initial_candles()
    
#     data = DataProcess()
#     data.delete_candles_recursive()

    from app.controllers.bitflyer.streamdata import stream
    streamThread = Thread(target=stream.stream_ingestion_data)
    streamThread.start()
    streamThread.join()
