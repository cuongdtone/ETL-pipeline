# -*- coding: utf-8 -*-
# @Organization  : TMT
# @Author        : Cuong Tran
# @Time          : 2/13/2023

import os
import json
from kafka import KafkaProducer


def serializer(message):
    return json.dumps(message).encode('utf-8')


class KafkaHandler:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVER')],
            value_serializer=serializer
        )
        self.topic = os.getenv('KAFKA_TOPIC')

    def send(self, item):
        try:
            print(item)
            self.producer.send(self.topic, item)
        except Exception as e:
            print(e)


