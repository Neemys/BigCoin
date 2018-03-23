import sys
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SparkSession
import json
from elasticsearch import Elasticsearch
from datetime import datetime

spark = SparkSession \
    .builder \
    .appName("SparkStreamKafka") \
    .config("master", "local[2]") \
    .getOrCreate()

sc = spark.sparkContext


def addElastic(jsonObject):
    date = datetime.strptime(jsonObject["time"]["updated"], "%b %d, %Y %H:%M:%S %Z")
    rate = jsonObject["bpi"]["USD"]["rate_float"]
    devise = jsonObject["bpi"]["USD"]["code"]
    es = Elasticsearch([{'host': sys.argv[1], 'port': sys.argv[2]}])
    es.index(index='bitcoin_cours', doc_type='cours', body={'date': date, 'rate': rate, 'devise': devise})


def sendData(tuple):
    text = tuple[1].encode("utf-8")
    jsonObj = json.loads(text)
    print jsonObj["time"]["updated"]
    print jsonObj["bpi"]["USD"]["rate"]
    print jsonObj["bpi"]["USD"]["code"]

    addElastic(jsonObj)


def sendDataToElastic(rdds):
     rdds.foreach(lambda rdd: sendData(rdd))


def main():

    ssc = StreamingContext(sc, 10)

    broker, topic = sys.argv[3:]

    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": broker})

    kvs.foreachRDD(sendDataToElastic)

    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()
