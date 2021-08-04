import logging
import sys
from threading import Thread

from app.controllers.streamdata import stream
from app.controllers.initialprocess import InitialProcess

logging.basicConfig(filename="console.log",level=logging.INFO)
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)


if __name__ == "__main__":
    initial = InitialProcess()
    initial.set_initial_candles()
            
    streamThread = Thread(target=stream.stream_ingestion_data)
    streamThread.start()
    streamThread.join()