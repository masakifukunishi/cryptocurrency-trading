import sys
from threading import Thread
import logging

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)
# logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)

from app.controllers.gmo.streamdata import stream

if __name__ == "__main__":
    streamThread = Thread(target=stream.stream_ingestion_data)
    streamThread.start()
    streamThread.join()