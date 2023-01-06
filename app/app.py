import logging
import os
import queue
from datetime import datetime

from app import receiver, strategy

logging.warning("starting petrosa-strategy-gapfinder | ver.:  " + 
                                                    os.environ.get('VERSION', "0.0.0"))


start_datetime = datetime.utcnow()
le_queue = queue.Queue()

rec = receiver.PETROSAReceiver('binance_socket_raw', le_queue)

strat = strategy.Strategy()

while True:
    strat.run(le_queue)
