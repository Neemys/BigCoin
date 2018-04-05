import sys
import os
import elasticsearch
from elasticsearch import helpers


class BCElasticsearch:
    _es = None

    def __init__(self):

        # Try to get actual value from environment vars
        user = os.environ["ES_ADMIN_USER"] if ("ES_ADMIN_USER" in os.environ) else None
        password = os.environ["ES_ADMIN_PASS"] if "ES_ADMIN_PASS" in os.environ else None
        host = os.environ["ES_HOST"] if "ES_HOST" in os.environ else "localhost"
        port = os.environ["ES_PORT"] if "ES_PORT" in os.environ else 9200
        http_auth = (user, password) if (user is not None and password is not None) else None
        try:
            self._es = elasticsearch.Elasticsearch([host], http_auth=http_auth, port=port, scheme='http')
        except elasticsearch.ConnectionTimeout:
            sys.exit(50)

    # Try to get records from kafka, return a list of message
    def send_messages(self, generator):
        try:
            elasticsearch.helpers.bulk(self._es, generator)
        except elasticsearch.ConnectionTimeout:
            sys.exit(50)

    # Get a list of dictionary of results from ES using a query
    def get_data_from_query(self, index, query):
        try:
            res = self._es.search(index=index, body=query)
            return res["hits"]["hits"]
        except elasticsearch.ConnectionTimeout:
            sys.exit(50)

    # Delete data from ES using a query
    def delete_data_from_query(self, index, query):
        try:
            self._es.delete_by_query(index=index, body=query)
        except elasticsearch.ConnectionTimeout:
            sys.exit(50)
