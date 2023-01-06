import base64
import json
import logging
import os
import bson.json_util as json_util

import newrelic.agent
import requests

from app import data_manager


class Strategy(object):
    def __init__(self) -> None:
        self.dm = data_manager.DataManager()

    @newrelic.agent.background_task()
    def calc_diff(self, current, previous):
        diff = ((current / previous)-1) * 100
        return diff

    @newrelic.agent.background_task()
    def request_it(self, request) -> None:
        
        request = base64.b64encode(bytes(json.dumps(request), "utf-8"))
        request = request.decode()
        send_data ={"message": {"data": request}}
        send_data = json.dumps(send_data)
        
        
        logging.warning(send_data)
        
        resp = requests.post(
                             os.environ.get('BINANCE_ORDERS_ENDPOINT', ""), 
                             data=send_data
                             )
        
        logging.warning(resp.text)
        

    @newrelic.agent.background_task()
    def build_request(self, ticker, type, price, stop_loss_p, take_profit_p):
        token = f"{os.environ.get('BINANCE_API_KEY')};{os.environ.get('BINANCE_API_SECRET')}"

        price = float(price)
        stop_loss_p = float(stop_loss_p)
        take_profit_p = float(take_profit_p)


        if type == "BUY":
            stop_loss = price * (1 - (stop_loss_p / 100))
            take_profit = price * (1 + (take_profit_p / 100))
        if type == "SELL":
            stop_loss = price * (1 + (stop_loss_p / 100))
            take_profit = price * (1 - (take_profit_p / 100))
        else:
            logging.error("wrong stops bruh")
            return False


        data = {
            "token": token,
            "ticker": ticker,
            "type": type,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            # "valid_until": "2022-12-31T19:00:00"
        }
        return data


    @newrelic.agent.background_task()
    def actuator(self, ticker, period, diff, current_kline):
        bt = self.dm.get_result_bt(ticker, period)

        price = current_kline['close']

        if bt is None:
            logging.info("No backtests for this: " + str(ticker) + ' ' + str(period) + ' ' + str(diff))
            return False

        TRADES = 5
        SQN = 1

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

        if (diff < 0 and 
            diff > (-1 * bt["buy_threshold"]) and 
            bt['# Trades'] > TRADES and bt['SQN'] > SQN):
            
            req = self.build_request(ticker,
                                     "BUY", 
                                     price, 
                                     bt["buy_sl"], 
                                     bt["buy_tp"])
            if req is not False:
                logging.warning('BT | ' + json_util.dumps(bt))
                logging.warning('BUY Request | ' + json.dumps(req))
                
                self.request_it(req)
            
        elif (diff > 0 and 
              diff > bt["sell_threshold"] and 
              bt['# Trades'] > TRADES and 
              bt['SQN'] > SQN):
            req = self.build_request(ticker,
                                     "SELL",
                                     price,
                                     bt["sell_sl"],
                                     bt["sell_tp"])

            if req is not False:
                logging.warning('BT | ' + json_util.dumps(bt))
                logging.warning('SELL Request | ' + json.dumps(req))
                self.request_it(req)

        else:
            # logging.warning('didnt reach params' + json.dumps(params))
            pass

    @newrelic.agent.background_task()
    def run(self, msg_queue) -> None:
        msg = msg_queue.get()
        decoded = self.dm.decode_msg(msg)

        try:
            previous_kline = self.dm.get_previous_kline(
                decoded['symbol'], decoded['period'], decoded['kline_date'])

            if not previous_kline:
                logging.warn('Could not find previous candle')
                return None

            diff = self.calc_diff(float(decoded['close']), 
                                        float(previous_kline['close']))

            self.actuator(decoded['symbol'], decoded['period'], diff, decoded)
        except Exception as e:
            logging.warning(decoded)
            logging.error(e)

