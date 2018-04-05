import sys
import kafka
from kafka.errors import KafkaTimeoutError


# Create a KafkaProducer with the given client_id and send to the topic all data given by the generator.
# The generator should send three value each time :
# * message : a string to send to the topic
# * key : bytes (or be serializable to bytes via configured key_serializer) the key of the message (for partitionning)
# * timestamp_ms : int that represent the time for the message in epoch milliseconds (from Jan 1 1970 UTC)
# Exit if kafka timeout timed out
def send_to_topic_from_generator(topic,client_id,generator):
	try:
		kafka_producer = kafka.KafkaProducer(client_id=client_id,acks='all',retries=0, linger_ms=100)
		while True:
			message,key,timestamp_ms = generator.next()
			kafka_producer.send(topic=topic,value=message,key=key,timestamp_ms=timestamp_ms)

	except KafkaTimeoutError:
		sys.exit(30) #Kafka timeout
	except StopIteration:
		kafka_producer.close()


class BCKafkaConsumer:

	_consumer = None

	def __init__(self,topic,client_id):
		self._consumer = kafka.KafkaConsumer(topic, client_id=client_id, group_id=client_id, enable_auto_commit=False,auto_offset_reset='earliest')

	def __del__(self):
		self._consumer.close(autocommit=False)
		
	# Try to get records from kafka, return a list of message
	def get_messages(self):
		partitions_records = self._consumer.poll(timeout_ms=1000)
		list_value = []
		for partition in partitions_records:
			for record in partitions_records[partition]:
				list_value.append(record.value)
		return list_value

	def set_messages_read(self):
		self._consumer.commit()
