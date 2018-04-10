from bigcoin import bc_kafka,bc_elasticsearch
import json
import datetime
import signal

def generate_elastic_insert_from_messages(messages):
	for message in messages:
		json_message = json.loads(message)
		#value are in satoshi
		yield {
			'_index' : 'mineur_idx',
			'_type': 'transaction',
			'_id': json_message['index']+json_message['n'],
			'_source': {
				'date': datetime.datetime.utcfromtimestamp(json_message['timestamp']),
				'value': float(json_message["value"])/ 100000000,
				'address': json_message["addr"],
				'data_type': 'historique'
			}
		}

def main():

	bc_consumer = bc_kafka.BCKafkaConsumer("historique_mineurs","python_historique_mineurs_consumer")
	bc_es = bc_elasticsearch.BCElasticsearch()
	while True:
		messages = bc_consumer.get_messages()
		if len(messages) == 0:
			break
		bc_es.send_messages(generate_elastic_insert_from_messages(messages))
		bc_consumer.set_messages_read()

	#Wait forever for a restart (will be killed then restarted)
    signal.pause()
    
if __name__ == '__main__':
	main()
