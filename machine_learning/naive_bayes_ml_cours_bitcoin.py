import sys
import datetime
from datetime import timedelta
from pyspark.sql import SparkSession, Row
from pyspark.ml.feature import CountVectorizer, StringIndexer
from pyspark.ml.classification import NaiveBayes, NaiveBayesModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import Pipeline, PipelineModel
import requests
from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Stopwords list and char to remove for formatting text
STOPWORDS = set(stopwords.words('english'))
CHAR_TO_REMOVE = ',.:;?!"()'
# API key for GoogleNews API
API_KEYS = 'your API key'
API_KEYS = sys.argv[1]
# Weight for splitting data in training data and testing data 
SPLIT_WEIGHT = 0.7
# default values for elasticseach
es_host = 'localhost' 
es_port = 9200
es_index = 'cours_btc_idx_ml'
es_doc_type = 'cours_btc_ml'
# Date search for prediction, one day or range
date_predict = '2018-03-29'
date_predict_end = ''
if (len(sys.argv) >= 3):
	date_predict = sys.argv[2]
if (len(sys.argv) >= 4):
	date_predict_end = sys.argv[3]
# Model path to save or load NaiveBayes model
model_path = "./model"

#Initialize SparkSession
spark = SparkSession \
	.builder \
	.appName("Machine learning Bitcoin") \
	.config("master", "local[3]") \
	.getOrCreate()
sc = spark.sparkContext

def get_next_day(date_str):
	date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
	next_day = date + timedelta(days=1)
	next_date_str = next_day.strftime("%Y-%m-%d")
	return next_date_str
		
def retrieve_bitcoin_cours(date_str):
	es = Elasticsearch([{'host': es_host, 'port': es_port}])
	res = es.get(index=es_index, doc_type=es_doc_type, id=date_str)
	return res

def retrieve_raw_data_day(date_str):
	date_early = date_str+'T00:00:00'
	date_late = date_str+'T23:59:59'
	url_googlenews_api = ('https://newsapi.org/v2/everything?'
       'q=Bitcoin&'
	   'language=en&'
       'from='+date_early+'&'
	   'to='+date_late+'&'
       'sortBy=relevance&'
	   'pageSize=100&'
	   'page=1&'
       'apiKey='+API_KEYS)
	  
	response = requests.get(url_googlenews_api)
	if response.status_code == 200:
		return response.json()
	else:
		# print ('error')
		return None
		# sys.exit(20)

#To do: filter number
def filter_text(text):
	#tokenize text
	list_mots = text.lower().split(' ')
	#filter ponctuations and stopwords
	list_mots = [mot.strip(CHAR_TO_REMOVE) for mot in list_mots]
	list_mots = [mot for mot in list_mots if mot not in STOPWORDS and mot.isalpha()]
	#lemmatize words
	wordnet_lemmatizer = WordNetLemmatizer()
	list_mots = [wordnet_lemmatizer.lemmatize(mot) for mot in list_mots]
	list_mots = [wordnet_lemmatizer.lemmatize(mot, pos='v') for mot in list_mots]
	return list_mots

def get_aggregated_text(formatted_data):
	aggregated_mots = []
	for i in formatted_data:
		date, list_mots = i
		aggregated_mots += list_mots
	return aggregated_mots

def format_data(raw_data):
	formatted_data = []
	for i in range (len(raw_data['articles'])):
		text_article = (raw_data["articles"][i]["title"])
		#text_article = (raw_data["articles"][i]["description"])
		if text_article != None:
			formatted_words_list = filter_text(text_article)
			date_article = (raw_data["articles"][i]["publishedAt"])
			formatted_data.append((date_article, formatted_words_list))
	return formatted_data	
	
def split_data(rdd):
	(rdd_train, rdd_test) = rdd.randomSplit([SPLIT_WEIGHT, 1.0 - SPLIT_WEIGHT])
	return (spark.createDataFrame(rdd_train), spark.createDataFrame(rdd_test))
	
def get_data_day(date_str):
	data_search = retrieve_raw_data_day(date_str)
	if data_search != None:
		formatted_data_search = format_data(data_search)
		if formatted_data_search != None:
			data_list_search = get_aggregated_text(formatted_data_search)
			# diff_day = get_variation_value(date_str, get_next_day(date_str))
			# diff_wordslist_search = (diff_day, data_list_search)
			return data_list_search
	return None
	
def get_variation_value(date_str, date_next_str):
	date = date_str
	date_suiv = date_next_str
	bitcoin_data_date = (retrieve_bitcoin_cours(date))
	valeur_day = bitcoin_data_date["_source"]["rate"]
	
	bitcoin_data_date = (retrieve_bitcoin_cours(date_suiv))
	valeur_day_next = bitcoin_data_date["_source"]["rate"]
	
	difference = valeur_day_next - valeur_day
	return float(1) if difference >= 0 else float(0)

def train_naive_bayes_model():
	# Date range for retrieving data
	date_start = '2018-02-01'
	date_end = '2018-03-01'
	date_search = date_start
	# Create tuple (date, wordslist) containing date and list of words from articles
	tuples_list = []
	while (date_search != date_end):
		wordslist = get_data_day(date_search)
		if wordslist != None:
			diff = get_variation_value(date_search, get_next_day(date_search))
			diff_wordslist = (diff, wordslist)
			tuples_list.append(diff_wordslist)
		date_search = get_next_day(date_search)
	# Create dataframe from data retrieved
	rdd = sc.parallelize(tuples_list)
	rdd = rdd.map(lambda tuple: Row(diff=tuple[0], words=tuple[1]))
	df_train, df_test = split_data(rdd)
	
	print ('test')
	# Naive Bayes Model Pipeline : CountVectorizer, StringIndexer, NaiveBayes
	count_vectorizer = CountVectorizer(inputCol='words', outputCol='features')
	label_indexer = StringIndexer(inputCol='diff', outputCol='label_index')
	classifier = NaiveBayes(labelCol='label_index', featuresCol='features', predictionCol='label_predicted')
	
	pipeline = Pipeline(stages=[count_vectorizer, label_indexer, classifier])
	pipeline_model = pipeline.fit(df_train)
	# Save model in local fs
	model_path = "./model"
	pipeline_model.write().overwrite().save(model_path)
	print ("Save Model")
	# Apply model on test data
	test_predicted = pipeline_model.transform(df_test)
	
	# Evaluator
	# Evaluate prediction accuracy on test data
	evaluator = MulticlassClassificationEvaluator(labelCol='label_index', predictionCol='label_predicted', metricName='accuracy')
	accuracy = evaluator.evaluate(test_predicted)
	
	print ('Accuracy : '+ str(accuracy*100)+'%')

def predict_bitcoin_cours_date(date_predict_start, date_predict_end = ""):
	# Date range for retrieving data
	date_start = date_predict_start
	if date_predict_end == "":
		date_end = get_next_day(date_start)
	else:
		date_end = date_predict_end
	date_search = date_start
	# Create tuple (date, wordslist) containing date and list of words from articles
	table = []
	while (date_search != date_end):
		wordslist_predict = get_data_day(date_search)
		if wordslist_predict != None:
			tuple = (0.0, wordslist_predict, date_search)
			table.append(tuple)
		date_search = get_next_day(date_search)
	
	rdd_predict = sc.parallelize(table)
	rdd_predict = rdd_predict.map(lambda tuple: Row(diff=tuple[0], words=tuple[1], date_search=tuple[2]))
	df_predict = spark.createDataFrame(rdd_predict)
	
	#df_predict_vect = vectorizer_transformer.transform(df_predict)
	#df_predict = label_indexer_transformer.transform(df_predict_vect)
	#df_predicted = classifier_transformer.transform(df_predict)
	
	model_path = "./model"
	pipeline_model = PipelineModel.load(model_path)
	df_predicted = pipeline_model.transform(df_predict)
	
	#print ('Resultat prediction pour le jour '+date_predict)
	df_predicted.show()
	
def main():
	date_predict = '2018-03-31'
	date_predict_end = ''
	train_naive_bayes_model()
	predict_bitcoin_cours_date(date_predict, date_predict_end)

if __name__ == "__main__":
	main()
