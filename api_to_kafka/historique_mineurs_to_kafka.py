import requests
import datetime
import calendar
import sys
import bigcoin.date as bcdate
import bigcoin.persistence as bcpersist
from bigcoin import bc_kafka, webservice
import time

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=n)

# generate kafka message from list of messages
def generate_kafka_message_from_list(messages):
    for message in messages:
        yield message['message'],message['key'],message['timestamp_ms']

def main():
    filename = "historique_mineurs_to_kafka.bcdata"
    isLastDateReset = False
    #Check if we must reset the last date
    if (len(sys.argv) >= 2):
        isLastDateReset = sys.argv[1] == "reset"
    #default value for starting date
    start_date = datetime.datetime(2018,03,01)

    if not isLastDateReset:
    	maybe_start_date = bcpersist.get_date_from_file(filename)
    	maybe_start_date = bcdate.get_datetime_from_string(bcdate.increment_a_day_from_date_as_string(maybe_start_date))
    	if maybe_start_date is not None:
    		start_date = maybe_start_date

    end_date = datetime.datetime.today()

    # For each day in date range, send to kafka and update last day fetched
    for date_current_day in daterange(start_date, end_date):
        time.sleep(10) # need to wait 10 second per api request
        # get all block of the day
        url_blocks_of_the_day = 'https://blockchain.info/blocks/' + str(calendar.timegm(date_current_day.timetuple())*1000) + '?format=json'
        data_blocks = webservice.get_json_from_address(url_blocks_of_the_day)
        # get all wanted data from each block and create messages to send to kafka
        messages = []
        for i in range(len(data_blocks["blocks"])):
            time.sleep(10) # need to wait 10 second per api request
            url_current_block = 'https://blockchain.info/rawblock/' + str(data_blocks["blocks"][i]['hash'])
            current_block_data = webservice.get_json_from_address(url_current_block)
            if len(current_block_data['tx']) > 0:
                if 'out' in current_block_data['tx'][0]:
                    tx_index = current_block_data['tx'][0]['tx_index']
                    date_event_in_s = current_block_data['tx'][0]['time']
                    for input_tx in current_block_data['tx'][0]['out']:
                        if 'value' in input_tx and 'addr' in input_tx:
                            messages.append({'message':'{"index":"'+str(tx_index)+'","n":"'+str(input_tx['n'])+'","value":'+str(input_tx['value'])+',"addr":"'+str(input_tx['addr'])+'","timestamp":'+str(date_event_in_s)+'}','key':None,'timestamp_ms':None})
        # send messages to kafka
        bc_kafka.send_to_topic_from_generator("historique_mineurs","python_historique_mineurs_producer",generate_kafka_message_from_list(messages))
        #Set the last processed date
        bcpersist.save_date_to_file(filename,bcdate.get_date_string_yyyy_mm_dd_from_datetime(date_current_day))
if __name__ == '__main__':
    main()
