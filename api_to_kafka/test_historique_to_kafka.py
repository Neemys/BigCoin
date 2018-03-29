
try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2, install from pip first
    import mock
import unittest
from historique_to_kafka import *
import json

class HistoriqueToKafkaTest(unittest.TestCase):

	def test_generate_data_for_kafka_from_json(self):
		#test normal json
		obj = {'bpi': {'2011-01-01': 0.2243, '2011-01-02': 0.2243}, 'disclaimer': 'This data was produced from the CoinDesk Bitcoin Price Index. BPI value data returned as EUR.', 'time': {'updated': 'Jan 3, 2011 00:03:00 UTC', 'updatedISO': '2011-01-03T00:03:00+00:00'}}
		#currency is a variable defined in historique_to_kafka
		expected_results = [
			{
				'message': {
					'date':'2011-01-01',
					'amount': 0.2243,
					'currency':currency
				},
				'key':None,
				'timestamp_ms':1293836400000.0
			},
			{
				'message': {
					'date':'2011-01-02',
					'amount': 0.2243,
					'currency':currency
				},
				'key':None,
				'timestamp_ms':1293922800000.0
			}

		]
		for message,key,timestamp_ms in generate_data_for_kafka_from_json(obj):
			#Since we can't infer the result order, we need to find if it exist in our list of result, assert everything and remove it
			isFound = False
			message = json.loads(message)
			for value in expected_results:
				if value['message'] == message:
					isFound = True
					self.assertEqual(key,value['key'])
					self.assertEqual(timestamp_ms,value['timestamp_ms'])
					expected_results.remove(value)
					break
			assert isFound
		#test empty json
		json2 = {}
		sendNothing = False
		try:
			generate_data_for_kafka_from_json(json2).next()
		except StopIteration:
			sendNothing = True
		assert sendNothing
		#test not json
		json3 = 87
		sendNothing2 = False
		try:
			generate_data_for_kafka_from_json(json3).next()
		except StopIteration:
			sendNothing2 = True
		assert sendNothing2

		def  test_is_date_webservice_valid(self):
			self.assertTrue(is_date_webservice_valid("2011-05-22"))
			self.assertFalse(is_date_webservice_valid("2011.05.22"))
			self.assertFalse(is_date_webservice_valid("2011_05_22"))
			self.assertFalse(is_date_webservice_valid("11-05-22"))
			self.assertFalse(is_date_webservice_valid("2011-5-22"))
			self.assertFalse(is_date_webservice_valid("2011-05-2"))
			self.assertFalse(is_date_webservice_valid(""))
			self.assertFalse(is_date_webservice_valid(54))

if __name__ == "__main__":
	unittest.main()