from kafka import KafkaConsumer
consumer = KafkaConsumer('binance_socket_raw',
                         group_id="local_dev",
                         bootstrap_servers='localhost:9093')
for msg in consumer:
    print(msg)
