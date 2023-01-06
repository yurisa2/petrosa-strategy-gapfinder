import datetime
import os

import newrelic.agent
import pymongo

from main import periods


class DataManager(object):
    def __init__(self) -> None:
        self.client = self.get_mongo_client()


    @newrelic.agent.background_task()
    def get_mongo_client(self):
        client = pymongo.MongoClient(
                    os.getenv(
                        'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
                    readPreference='secondaryPreferred',
                    appname='petrosa-strategy-gapfinder')
                    
        return client


    @newrelic.agent.background_task()
    def get_previous_kline(self, ticker, period, date_time):

        db = self.client["petrosa_crypto"]
        history = db["candles_" + periods[period]['suffix']]

        previous_date_time = date_time -  datetime.timedelta(minutes=periods[period]['minutes'])
        result = history.find_one(
                                    {'ticker': ticker, 
                                    'datetime': previous_date_time}, 
                                    ['datetime', 'close'])

        return result


    @newrelic.agent.background_task()
    def get_result_bt(self, ticker, period):
        db = self.client["petrosa_crypto"]
        col = db["backtest_results"]

        result = col.find_one(
            {'symbol': ticker, 
             'period': period, 
             'strategy': 'simple_gap_finder',
            })

        return result


    @newrelic.agent.background_task()
    def decode_msg(self, msg):
        kline_date = datetime.datetime.fromtimestamp(msg['k']['t']/1000)
        symbol = msg['k']['s']
        close = msg['k']['c']
        period = msg['k']['i']

        ret = {'kline_date': kline_date,
            'symbol': symbol,
            'close': close,
            'period': period
                }
        
        return ret

