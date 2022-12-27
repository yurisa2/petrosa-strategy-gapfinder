from datetime import datetime
import queue
from app import strategy
from app import receiver


start_datetime = datetime.utcnow()
le_queue = queue.Queue()

rec = receiver.PETROSAReceiver('binance_socket_raw', le_queue)
# strategy.gogo(le_queue)

strat = strategy.Strategy()

while True:
    strat.run(le_queue)
