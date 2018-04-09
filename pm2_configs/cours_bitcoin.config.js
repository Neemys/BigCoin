module.exports = {
	apps : [
	    {
			name      : 'api_to_kafka_cours_bitcoin_historic',
			script    : 'historique_to_kafka.py',
	    },
	    {
			name      : 'kafka_to_es_cours_bitcoin_historic',
			script    : 'kafka_historique_to_elastic.py',
	    },
	    {
			name      : 'api_to_kafka_cours_bitcoin_realtime',
			script    : 'price_index_to_kafka_realtime.py',
	    },
	    {
			name      : 'kafka_to_es_cours_bitcoin_realtime',
			script    : 'java',
	        args: [
	            "-jar",
	            "sparkStream-1.0.jar"
	        ],
			exec_interpreter:""
	    }
 	]
};
