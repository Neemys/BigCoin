from datetime import datetime,date,timedelta
import json
import sys
import struct
import os.path
import re
from bigcoin import bc_kafka, webservice
import calendar

# Global values
date_y_m_d_pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

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

# Test if a date format is valid for the webservice.
def is_date_webservice_valid(date_string):
	if date_y_m_d_pattern.match(date_string):
		return True
	return False


# Get a date from the first line of the file. Return the date in a valid format for the webservice, None otherwise.
def getDateFromFile(filepath_and_name):
	if(not os.path.isfile(filepath_and_name)):
		return None
	try:
		with open(filepath_and_name,'r') as f:
			maybe_date = f.readline()
	except IOError:
		sys.exit(40)# Exit with file error
	if is_date_webservice_valid(maybe_date):
		return maybe_date
	return None

# Save the given date string to the file
def saveDateToFile(date_string):
	try:
		with open(filename,'w') as f:
			f.write(date_string)
	except IOError:
		sys.exit(40)# Exit with file error

# Add a day to the given date as string and return the new date as string. If the date format is not valid, return None
def increment_a_day_from_date_as_string(date_string):
	if date_string  is not None and is_date_webservice_valid(date_string):
		year,month,day = date_string.split('-')
		new_date = datetime(int(year),int(month),int(day)) + timedelta(days=1)
		return get_date_string_from_datetime(new_date)
	return None

# Return the given datetime as a date valid for the webservice. return today's date if no datetime given
def get_date_string_from_datetime(date_time):
	if not isinstance(date_time,datetime):
		date_time = datetime.today()
	return date_time.strftime("%Y-%m-%d")

def main():
	global currency
	#The API don't go before that date, so it is the default one
	start_date = get_date_string_from_datetime(datetime(2010,07,17))
	end_date = get_date_string_from_datetime(datetime.today())

	if (len(sys.argv) >= 2):
		currency = sys.argv[1]

	# Get date from previous execution
	maybe_start_date = getDateFromFile(filename)
	maybe_start_date = increment_a_day_from_date_as_string(maybe_start_date)
	if maybe_start_date is not None:
		start_date = maybe_start_date
	url_cours_bitcoin = 'https://api.coindesk.com/v1/bpi/historical/close.json?currency='+currency+'&start='+start_date+'&end='+end_date
	json_data = webservice.get_json_from_address(url_cours_bitcoin)
	bc_kafka.send_to_topic_from_generator("historique_cours_bitcoin","python_historique_cours_bitcoin_producer",generate_data_for_kafka_from_json(json_data))
	saveDateToFile(end_date)

if __name__ == '__main__':
	main()
