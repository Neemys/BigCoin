
from bigcoin import bc_kafka,bc_elasticsearch
import json
import datetime
import signal
def generate_elastic_insert_from_messages(messages):
	for message in messages:
		json_message = json.loads(message)
		date_event = datetime.datetime.strptime(json_message["date"], "%Y-%m-%d").date()
		print "added for date "+json_message["date"]
		yield {
			'_index' : 'cours_btc_idx',
			'_type': 'cours_btc',
			'_id': date_event,
			'_source': {
				'date': date_event,
				'rate': json_message["amount"],
				'devise': json_message["currency"],
				'data_type': 'historique'
			}
		}
def main():

	bc_consumer = bc_kafka.BCKafkaConsumer("historique_cours_bitcoin","python_historique_cours_bitcoin_consumer")
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
