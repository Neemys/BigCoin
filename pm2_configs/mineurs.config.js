module.exports = {
	apps : [
	    {
			name      : 'api_to_kafka_mineurs_historic',
			script    : 'historique_mineurs_to_kafka.py',
	    },
	    {
			name      : 'kafka_to_es_mineurs_historic',
			script    : 'kafka_historique_mineurs_to_elastic.py',
	    },
	    {
			name      : 'api_to_kafka_mineurs_realtime',
			script    : 'mineur_to_kafka_realtime.py',
	    },
	    {
			name      : 'kafka_to_es_mineurs_realtime',
			script    : 'java',
	        args: [
	            "-jar",
	            "mineurToESRealtime-1.0.jar"
	        ],
			exec_interpreter:""
	    }
 	]
};
