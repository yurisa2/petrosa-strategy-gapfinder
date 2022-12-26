from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')

while True:
    producer.send('test', b'HOLD THE LINE')
