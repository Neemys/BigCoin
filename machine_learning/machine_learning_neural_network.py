import requests
import datetime
from datetime import date, timedelta
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
import math
from elasticsearch import Elasticsearch
from elasticsearch import helpers

model_path = './model_test'
currency = 'EUR'
date_start = '2010-07-17'
date_end = str(datetime.date.today())
host_es = "localhost"
port_es = 9200

def get_next_day(date_str):
	date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
	next_day = date + timedelta(days=1)
	next_date_str = next_day.strftime("%Y-%m-%d")
	return next_date_str

# Retrieve data from CoinDesk API
def get_historique_data(currency, start_date, end_date):	
	url_cours_bitcoin = 'https://api.coindesk.com/v1/bpi/historical/close.json?currency='+currency+'&start='+start_date+'&end='+end_date
	res = requests.get(url_cours_bitcoin)
	if res.ok:
		return res
	else:
		return None

def create_dataset(dataset):
  dataX, dataY = [], []
  for i in range(len(dataset)-1):
    dataX.append(dataset[i])
    dataY.append(dataset[i + 1])
  return np.asarray(dataX), np.asarray(dataY)

def create_LSTM_network():
	model = Sequential()
	model.add(LSTM(4, input_shape=(1,1)))
	model.add(Dense(1))
	model.compile(loss='mean_squared_error', optimizer='adam')
	return model
  
def save_model(model, model_path):
	model.save(model_path)

def predict_next_day(model, scaler, dataset_raw, testPredict):
	futurePredict = model.predict(np.asarray([[testPredict[-1]]]))
	futurePredict = scaler.inverse_transform(futurePredict)

	testPredict = scaler.inverse_transform(testPredict)
	# Predict value for the next day
	print ('Bitcoin value for tomorrow : ', futurePredict)		
	
def calculate_rmse(trainY, testY, trainPredict, testPredict):
	# Calculate root mean squared error (RMSE)
	trainScore = math.sqrt(mean_squared_error(trainY[:,0], trainPredict[:,0]))
	print('Train Score: %.2f RMSE' % (trainScore))
	testScore = math.sqrt(mean_squared_error(testY[:,0], testPredict[:,0]))
	print('Test Score: %.2f RMSE' % (testScore))		
	
def plot_comparison_curves(dataset, trainPredict, testPredict, scaler):
	# shift train predictions for plotting
	trainPredictPlot = np.empty_like(dataset)
	trainPredictPlot[:, :] = np.nan
	trainPredictPlot[1:len(trainPredict)+1, :] = trainPredict
	# shift test predictions for plotting
	testPredictPlot = np.empty_like(dataset)
	testPredictPlot[:, :] = np.nan
	testPredictPlot[len(trainPredict):len(dataset)-1, :] = testPredict
	
	# plot baseline and predictions
	plt.plot(scaler.inverse_transform(dataset))
	plt.plot(trainPredictPlot)
	plt.plot(testPredictPlot)
	plt.show()
	
def add_elastic(list, date):
	for i in range(len(list)):
		date_event = get_next_day(date[i])
		value_event = list[i][0]
		# print (date_event, value_event)
		yield {
			'_index' : 'cours_btc_idx_ml',
			'_type': 'cours_btc_ml',
			'_source': {
				'date': date_event,
				'rate_predicted': value_event,
				'devise': currency,
				'data_type': 'historique_predicted'
			}
		}
	
def main():
	# Get historical data from CoinDesk API
	data_historique = get_historique_data('EUR', date_start, date_end)
	data = data_historique.json()
	
	# Filter data to keep date and btc value
	dataset_raw = []
	date = []
	rate = []
	for i in data["bpi"]:
		# date_event = datetime.datetime.strptime(i, "%Y-%m-%d").date()
		date_event = i
		value_event = data["bpi"][i]
		date.append(date_event)
		rate.append(value_event)
		dataset_raw.append(value_event)
	
	# Normalize dataset
	dataset = np.asarray(dataset_raw).reshape(-1,1)
	scaler = MinMaxScaler(feature_range=(0,1))
	dataset = scaler.fit_transform(dataset)

	# Format data to fit input requirement for LSTM model
	# dataX : value at n_i, dataY : value at n_i+1
	dataX, dataY = create_dataset(dataset)
	
	# Split data into training data and testing data 80/20
	trainX, testX, trainY, testY = train_test_split(dataX, dataY, test_size=0.20, shuffle=False)
	
	# Reshape to fit input requirement for LSTM neural network (input_shape=(samples, timestep, features))
	trainX = np.reshape(trainX, (trainX.shape[0], 1, 1))
	testX = np.reshape(testX, (testX.shape[0], 1, 1))
	
	# Create LSTM Network
	model = create_LSTM_network()
	model.fit(trainX, trainY, epochs=5, batch_size=100, verbose=0)
	
	# Save model
	save_model(model, model_path)
	# Load model
	model = load_model(model_path)
	
	# Make predictions
	trainPredict = model.predict(trainX)
	testPredict = model.predict(testX)
	
	predict_next_day(model, scaler, dataset_raw, testPredict)
	
	# Invert predictions to get BTC value back 
	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform(trainY)
	testPredict = scaler.inverse_transform(testPredict)
	testY = scaler.inverse_transform(testY)

	list_train = trainPredict.tolist()
	list_test = testPredict.tolist()
	list = list_train + list_test
	
	# Connect to elastic search
	es = Elasticsearch([{'host': host_es, 'port': port_es}])
	# Add data in elastic search in bulk
	helpers.bulk(es, add_elastic(list, date))
	
	#calculate_rmse(trainY, testY, trainPredict, testPredict)
	# plot_comparison_curves(dataset, trainPredict, testPredict, scaler)
	
if __name__ == '__main__':
	main()