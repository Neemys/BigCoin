import requests
from elasticsearch import Elasticsearch
from datetime import date, timedelta
import datetime

host_es = 'localhost'
port_es = 9200
es = Elasticsearch([{'host': host_es, 'port': port_es}])

def search_date_elastic(date_str, list_value, list_predicted):
	res = es.search(index='cours_btc_idx_ml', doc_type='cours_btc_ml', body={"query": {"match": {"date": date_str}}})
	# print("%d documents found:" % res['hits']['total'])
	if res['hits']['total'] == 2:
		for doc in res['hits']['hits']:
			if 'rate' in doc['_source']:
				date_actual = doc['_source']['date']
				rate_actual = doc['_source']['rate']
				list_value.append(rate_actual)
				# list_value.append((date_actual, rate_actual))
				# print("%s %s" % (doc['_source']['date'], doc['_source']['rate']))
			elif 'rate_predicted' in doc['_source']:
				date_predicted = doc['_source']['date']
				rate_predicted = doc['_source']['rate_predicted']
				list_predicted.append(rate_predicted)
				# list_predicted.append((date_predicted, rate_predicted))
				# print ("%s %s" % (doc['_source']['date'], doc['_source']['rate_predicted']))
			
def get_next_day(date_str):
	date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
	next_day = date + timedelta(days=1)
	next_date_str = next_day.strftime("%Y-%m-%d")
	return next_date_str
			
def main():			
	list_value = []
	list_predicted = []
	start_date = '2018-03-01'
	end_date = '2018-04-01'
	search_date = start_date
	while search_date != end_date:
		search_date_elastic(search_date, list_value, list_predicted)
		search_date = get_next_day(search_date)
	# print (list_value)
	# print (list_predicted)
	
	cnt = 0
	for i in range (len(list_predicted)-1):
		diff_actual = list_value[i+1] - list_value[i]
		diff_predicted = list_predicted[i+1] - list_predicted[i]
		if (diff_actual >= 0 and diff_predicted >= 0) or (diff_actual <= 0 and diff_predicted <= 0):
			cnt += 1
	print ("Accuracy : "+str((float(cnt)/float(len(list_value)))*100))
	# es.delete_by_query(index="cours_btc_idx_ml", doc_type="cours_btc_ml", body={"query": {"match": {"data_type": "historique_predicted"}}})
	
if __name__ == '__main__':
	main()

			