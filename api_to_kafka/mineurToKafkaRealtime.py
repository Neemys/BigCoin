import requests
import time
from kafka import SimpleProducer, KafkaClient
import json


# Connect to Kafka
kafka = KafkaClient('localhost:9092')
producer = SimpleProducer(kafka)

# Assign a topic
topic = 'mineur-realtime'

while(1):
    # Get latest block ID
    latest_block = requests.get("https://blockchain.info/fr/latestblock")
    id_block = latest_block.json()["block_index"]
    print id_block

    # Get first transaction of block and send it to Kafka
    block = requests.get("https://blockchain.info/fr/rawblock/" + str(id_block))
    producer.send_messages(topic, str(block.text))

    # Wait for the next block
    while id_block == requests.get("https://blockchain.info/fr/latestblock").json()["block_index"]:
        time.sleep(60)
