import os
import logging
import json
import requests
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
    def build_request(self, ticker, type, price, stop_loss_p, take_profit_p):
        token = f"{os.environ.get('BINANCE_API_KEY')};{os.environ.get('BINANCE_API_SECRET')}"

        if type == "COMPRA":
            stop_loss = price + (price * (stop_loss_p/100))
            take_profit = price - (price * (take_profit_p/100))
        if type == "VENDA":
            stop_loss = price - (price * (stop_loss_p/100))
            take_profit = price + (price * (take_profit_p/100))


        data = {
            "token": token,
            "ticker": ticker,
            "type": type,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "valid_until": "2022-12-31T19:00:00"
        }
        return data


    @newrelic.agent.background_task()
    def actuator(self, ticker, period, diff, current_kline):
        bt = self.dm.get_result_bt(ticker, period)

        price = current_kline['close']

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

        if (diff > (-1 * bt["sell_threshold"]) and bt['# Trades'] > TRADES and bt['SQN'] > SQN):
            logging.warning('This should be a BUY ' + json.dumps(params))
            logging.warning('BUY Request ' + json.dumps(self.build_request(ticker,
                            'COMPRA', price, bt["buy_sl"], bt["buy_tp"])))
        elif (diff < bt["buy_threshold"] and bt['# Trades'] > TRADES and bt['SQN'] > SQN):
            logging.warning('This should be a SELLLLLL' + json.dumps(params))
            logging.warning('SELL Request ' + json.dumps(self.build_request(ticker,
                                                                            'VENDA', 
                                                                            price, 
                                                                            bt["sell_sl"], 
                                                                            bt["sell_tp"])))

        else:
            # logging.warning('didnt reach params' + json.dumps(params))
            pass


    @newrelic.agent.background_task()
    def run(self, msg_queue):
        msg = msg_queue.get()
        decoded = self.dm.decode_msg(msg)

        previous_kline = self.dm.get_previous_kline(
            decoded['symbol'], decoded['period'], decoded['kline_date'])

        diff = self.calc_diff(float(decoded['close']), 
                                    float(previous_kline['close']))

        self.actuator(decoded['symbol'], decoded['period'], diff, decoded)

