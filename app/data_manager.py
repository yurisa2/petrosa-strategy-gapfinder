import pymongo
import os


def get_client():
    client = pymongo.MongoClient(
                os.getenv(
                    'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
                readPreference='secondaryPreferred',
                appname='petrosa-strategy-gapfinder')
                
    return client


def get_data(ticker, period, limit=2):

    if(period == '5m'):
        suffix = 'm5'
    if(period == '15m'):
        suffix = 'm15'
    if(period == '30m'):
        suffix = 'm30'
    if(period == '1h'):
        suffix = 'h1'

    client = get_client()

    db = client["petrosa_crypto"]
    history = db["candles_" + suffix]

    results = history.find({'ticker': ticker}, ['datetime', 'close'],
                           sort=[('datetime', -1)]).limit(limit)
    results_list = list(results)

    return results_list
