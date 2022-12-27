import logging
import json
import newrelic.agent
from app import data_manager


class Strategy(object):
    def __init__(self) -> None:
        self.dm = data_manager.DataManager()


    @newrelic.agent.background_task()
    def calc_diff(self, current, previous):
        diff = ((current / previous) - 1) * 100
        
        return diff


    @newrelic.agent.background_task()
    def actuator(self, ticker, period, diff):
        bt = self.dm.get_result_bt(ticker, period)

        if bt is None:
            logging.info("No backtests for this: " + str(ticker) + ' ' + str(period) + ' ' + str(diff))
            return False

        TRADES = 1000
        SQN = 2

        params = {}
        params['ticker'] = ticker
        params['period'] = period
        params['diff'] = diff
        params["buy_sl"] = bt["buy_sl"]
        params["buy_threshold"] = bt["buy_threshold"]
        params["buy_tp"] = bt["buy_tp"]
        params["sell_sl"] = bt["sell_sl"]
        params["sell_threshold"] = bt["sell_threshold"]
        params["sell_tp"] = bt["sell_tp"]

        if (diff > 0 and diff > (-1 * bt["sell_threshold"]) and bt['# Trades'] > TRADES and bt['SQN'] > SQN):
            logging.warning('lets do this' + json.dumps(params))
        elif (diff < 0 and diff < bt["buy_threshold"] and bt['# Trades'] > TRADES and bt['SQN'] > SQN):
            logging.warning('lets do this' + json.dumps(params))
        else:
            logging.warning('didnt reach params' + json.dumps(params))


    @newrelic.agent.background_task()
    def run(self, msg_queue):
        msg = msg_queue.get()
        decoded = self.dm.decode_msg(msg)

        previous_kline = self.dm.get_previous_kline(
            decoded['symbol'], decoded['period'], decoded['kline_date'])

        diff = self.calc_diff(float(decoded['close']), 
                                    float(previous_kline['close']))
        self.actuator(decoded['symbol'], decoded['period'], diff)

