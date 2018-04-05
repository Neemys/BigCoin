from bigcoin import bc_elasticsearch
import sys


# Get date of latest historic value
def get_latest_historic_date(es, index):
    query = {"query": {"match": {"data_type": "historique"}},
             "size": 1,
             "sort": [
                 {
                     "date": {
                         "order": "desc"
                     }
                 }
             ]}
    res = es.get_data_from_query(index, query)
    if len(res) > 0:
        return res[0]["_source"]["date"]
    else:
        return "2000-01-01T08:50:00"


# Delete realtime value older than latest historic value
def delete_realtime(es, index):

    date = get_latest_historic_date(es, index)
    query = {"query": {
        "bool": {
            "must": {
                "match": {
                    "data_type": "temps_reel"
                }
            },
            "filter": {
                "range": {"date": {"lte": date}}
            }
        }
    }}
    es.delete_data_from_query(index, query)


def main():
    bc_es = bc_elasticsearch.BCElasticsearch()
    es_index = sys.argv[1]

    delete_realtime(bc_es, es_index)


if __name__ == '__main__':
    main()
