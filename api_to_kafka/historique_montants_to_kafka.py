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

    api_key = ''
    with open('blockchain.info.key') as f:
        api_key = f.read()
    filename = "historique_montants_to_kafka.bcdata"
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
        url_blocks_of_the_day = 'https://blockchain.info/blocks/' + str(calendar.timegm(date_current_day.timetuple())*1000) + '?format=json&api_code='+api_key
        data_blocks = webservice.get_json_from_address(url_blocks_of_the_day)
        # get all wanted data from each block and create messages to send to kafka
        messages = []
        for i in range(len(data_blocks["blocks"])):
            time.sleep(10) # need to wait 10 second per api request
            url_current_block = 'https://blockchain.info/rawblock/' + str(data_blocks["blocks"][i]['hash'])+'?api_code='+api_key
            current_block_data = webservice.get_json_from_address(url_current_block)
            for j in range(len(current_block_data['tx'])):
                if 'inputs' in current_block_data['tx'][j]:
                    tx_index = current_block_data['tx'][j]['tx_index']
                    date_event_in_s = current_block_data['tx'][j]['time']
                    value_tx_in_satoshi = 0
                    for input_tx in current_block_data['tx'][j]['inputs']:
                        if 'prev_out' in input_tx:
                            value_tx_in_satoshi += input_tx['prev_out']['value']
                    if value_tx_in_satoshi != 0:
                        messages.append({'message':'{"index":"'+str(tx_index)+'","value":'+str(value_tx_in_satoshi)+',"timestamp":'+str(date_event_in_s)+'}','key':None,'timestamp_ms':date_event_in_s*1000})
        # send messages to kafka
        bc_kafka.send_to_topic_from_generator("historique_montants","python_historique_montants_producer",generate_kafka_message_from_list(messages))
        #Set the last processed date
        bcpersist.save_date_to_file(filename,bcdate.get_date_string_yyyy_mm_dd_from_datetime(date_current_day))
if __name__ == '__main__':
    main()
