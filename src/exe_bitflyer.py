import logging
import sys
from threading import Thread

from app.controllers.bitflyer.streamdata import stream
from app.controllers.initialprocess import InitialProcess
from app.controllers.dataprocess import DataProcess

format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(filename="console.log",level=logging.INFO, format=format)
# logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)


if __name__ == "__main__":
    initial = InitialProcess()
    initial.set_initial_candles()
    
#     data = DataProcess()
#     data.delete_candles_recursive()

    streamThread = Thread(target=stream.stream_ingestion_data)
    streamThread.start()
    streamThread.join()
    

# import logging
# import sys
# from threading import Thread

# from app.controllers.streamdata import stream
# from app.controllers.initialprocess import InitialProcess
# from app.controllers.dataprocess import DataProcess

# format = "%(asctime)s %(levelname)s %(name)s :%(message)s"
# logging.basicConfig(filename="console.log",level=logging.INFO, format=format)
# # logging.basicConfig(level=logging.INFO, stream=sys.stdout, format=format)


# if __name__ == "__main__":
#     initial = InitialProcess()
#     initial.set_initial_candles()
    
# #     data = DataProcess()
# #     data.delete_candles_recursive()

#     data = DataProcess()
#     dataThread = Thread(target=data.delete_candles_recursive)
#     streamThread = Thread(target=stream.stream_ingestion_data)
    
#     dataThread.start()
#     streamThread.start()
    
#     dataThread.join()
#     streamThread.join()