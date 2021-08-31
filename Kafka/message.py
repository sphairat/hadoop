#!/usr/bin/python2.7

from time import sleep
from json import dumps
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['172.17.17.32:6667'],
                         value_serializer=lambda x:
                         dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number' : e}
    producer.send('message', value=data)
    sleep(5)