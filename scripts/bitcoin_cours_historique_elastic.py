import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import date
import datetime
import json
import sys

def add_elastic():
	for i in data["bpi"]:
		date_event = datetime.datetime.strptime(i, "%Y-%m-%d").date()
		value_event = data["bpi"][i]
		yield {
			"_index" : "cours_btc_idx_gen",
			"_type": "cours_btc_gen",
			"_source": {
				"timestamp": date_event,
				"value": value_event
			}
		}

host = sys.argv[1]
port = sys.argv[2]
# Retrieve data from API
url_cours_bitcoin = 'https://api.coindesk.com/v1/bpi/historical/close.json?start=2011-01-01&end=2018-03-20'
res = requests.get(url_cours_bitcoin)
data = res.json()
# Connect to elastic search
es = Elasticsearch([{'host': host, 'port': port}])
# Add data in elastic search
helpers.bulk(es, add_elastic())
