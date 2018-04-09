from datetime import datetime,date,timedelta
import json
import sys
from bigcoin import bc_kafka, webservice
import calendar
import bigcoin.date as bcdate
import bigcoin.persistence as bcpersist


# Default values
filename = "historique_to_kafka.bcdata"
currency = 'EUR'

# Take all info from JSon object (dict) and add all to kafka
def generate_data_for_kafka_from_json(json_data):
	if type(json_data) is dict and json_data.has_key("bpi"):
		for date, amount in json_data["bpi"].iteritems():
			year,month,day = date.split('-')
			timestamp = calendar.timegm(datetime(int(year),int(month),int(day),0,0,0,0).timetuple())
			data_to_send = {
				'date':date,
				'amount':amount,
				'currency':currency
			}
			yield json.dumps(data_to_send),None,timestamp*1000



def main():
	global currency
	#The API don't go before that date, so it is the default one
	start_date = bcdate.get_date_string_yyyy_mm_dd_from_datetime(datetime(2010,07,17))
	end_date = bcdate.get_date_string_yyyy_mm_dd_from_datetime(datetime.today())
	if (len(sys.argv) >= 2):
		currency = sys.argv[1]

	# Get date from previous execution
	maybe_start_date = bcpersist.get_date_from_file(filename)
	maybe_start_date = bcdate.increment_a_day_from_date_as_string(maybe_start_date)
	if maybe_start_date is not None:
		start_date = maybe_start_date
	url_cours_bitcoin = 'https://api.coindesk.com/v1/bpi/historical/close.json?currency='+currency+'&start='+start_date+'&end='+end_date
	json_data = webservice.get_json_from_address(url_cours_bitcoin)
	bc_kafka.send_to_topic_from_generator("historique_cours_bitcoin","python_historique_cours_bitcoin_producer",generate_data_for_kafka_from_json(json_data))
	bcpersist.save_date_to_file(filename,end_date)

if __name__ == '__main__':
	main()
