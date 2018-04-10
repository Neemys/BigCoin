module.exports = {
	apps : [
	    {
			name      : 'api_to_kafka_montants_historic',
			script    : 'historique_montants_to_kafka.py',
	    },
	    {
			name      : 'kafka_to_es_montants_historic',
			script    : 'kafka_historique_montants_to_elastic.py',
	    },
	    {
			name      : 'api_to_kafka_montants_realtime',
			script    : 'transaction_to_kafka_realtime.py',
	    },
	    {
			name      : 'kafka_to_es_montants_realtime',
			script    : 'java',
	        args: [
	            "-jar",
	            "transactionToESRealtime-1.0.jar"
	        ],
			exec_interpreter:""
	    }
 	]
};
