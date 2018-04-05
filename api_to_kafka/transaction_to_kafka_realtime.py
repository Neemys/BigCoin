from websocket import create_connection
import requests
import time
from kafka import SimpleProducer, KafkaClient


# Connect to Kafka
kafka = KafkaClient('localhost:9092')
producer = SimpleProducer(kafka)

# Assign a topic
topic = 'transaction-realtime'


ws = create_connection("wss://ws.blockchain.info/inv")

ws.send("{\"op\":\"unconfirmed_sub\"}")

# Send message
while(1):
    result = ws.recv()
    producer.send_messages(topic, result)

ws.close()