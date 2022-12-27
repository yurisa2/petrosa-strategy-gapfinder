import os
from datetime import datetime
import queue
import logging
from app import strategy
from app import receiver

logging.warning("starting petrosa-strategy-gapfinder | ver.:  " + 
                                                    os.environ.get('VERSION'))


start_datetime = datetime.utcnow()
le_queue = queue.Queue()

rec = receiver.PETROSAReceiver('binance_socket_raw', le_queue)

strat = strategy.Strategy()

while True:
    strat.run(le_queue)
