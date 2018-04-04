import requests
from datetime import date, timedelta
import datetime
import time
import json
import sys
from kafka import KafkaProducer

# Default values
date_search = str(datetime.date.today())

# Input values
# date to search data for
if (len(sys.argv) >= 2):
    date_search = sys.argv[1]


def get_single_block(block_id):
    url_block = 'https://blockchain.info/rawblock/' + str(block_id)
    res_block = requests.get(url_block)
    if res_block.status_code == 200:
        return res_block
    else:
        return None


def get_blocks_for_day(date_blocks_in_ms):
    url_blocks = 'https://blockchain.info/blocks/' + str(date_blocks_in_ms) + '?format=json'
    res_blocks = requests.get(url_blocks)
    if res_blocks.ok:
        return res_blocks
    else:
        return None


def get_transactions_from_block(data_block):
    for i in range(len(data_block['tx'])):
        if 'inputs' in data_block['tx'][i]:
            if 'prev_out' in data_block['tx'][i]['inputs'][0]:
                tx_index = data_block['tx'][i]['inputs'][0]['prev_out']['tx_index']
                value_tx_in_satoshi = data_block['tx'][i]['inputs'][0]['prev_out']['value']

                date_event_in_ms = data_block['tx'][i]['time']
                date_event = datetime.datetime.fromtimestamp(date_event_in_ms)
                yield {
                    '_index': 'montants_tx_idx_test',
                    '_type': 'montants_tx_test',
                    '_id': tx_index,
                    '_source': {
                        'date': date_event,
                        'tx_index': tx_index,
                        'valeur_tx': float(value_tx_in_satoshi) / 100000000,
                    }
                }


def convert_date_in_ms(date):
    # timestamp = int(time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()))
    timestamp = int(time.mktime(date.timetuple()))
    date_in_ms = (timestamp + 3600) * 1000
    return date_in_ms


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def main():

    # Connect to Kafka
    producer = KafkaProducer(acks=1, max_request_size=10000000, bootstrap_servers='localhost:9092')

    # Assign a topic
    topic = 'transaction-historique'

    # Date range to get data from
    date_search = datetime.datetime.strptime('2018-03-25', "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime('2018-01-01', "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime('2018-03-20', "%Y-%m-%d").date()

    # For each day in date range, send each block to Kafka
    for single_date in daterange(start_date, end_date):

        res_blocks = get_blocks_for_day(convert_date_in_ms(single_date))
        data_blocks = res_blocks.json()

        for i in range(len(data_blocks["blocks"])):

            res = get_single_block(data_blocks["blocks"][i]['hash'])
            if (res != None):
                data = res.json()
                producer.send(topic, str(data))


if __name__ == '__main__':
    main()
