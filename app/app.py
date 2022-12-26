from datetime import datetime
from app import data_manager
from app import strategy



start_datetime = datetime.utcnow()

data_list = data_manager.get_data('BTCUSDT', '1h', 2)

# print(data_manager.get_data('BTCUSDT', '15m', 2)[0])
# print(data_manager.get_data('BTCUSDT', '15m', 2)[1])

print(strategy.calc_diff(data_list))