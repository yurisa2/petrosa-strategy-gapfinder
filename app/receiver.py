import os
import json
import threading
import logging
from kafka import KafkaConsumer
import newrelic.agent


class PETROSAReceiver(object):
    @newrelic.agent.background_task()
    def __init__(self,
                 topic,
                 petrosa_queue
                 ):

        self.petrosa_queue = petrosa_queue
        try:
            self.consumer = KafkaConsumer(topic,
                                          bootstrap_servers=os.getenv(
                                              'KAFKA_SUBSCRIBER', '127.0.0.1:9093'),
                                          group_id='petrosa-strategy-gapfinder'
                                          )
        except:
            logging.error('Error in Kafka Consumer')
            os._exit(1)

        logging.warning('Started receiver on topic: ' +  topic)
        threading.Thread(target=self.run).start()


    @newrelic.agent.background_task()
    def run(self):
        for msg in self.consumer:
            try:    
                msg = json.loads(msg.value.decode())
                self.petrosa_queue.put(msg)

            except:
                msg = msg.value.decode()
                logging.error('Not a Json or something else')
                raise

        return True
