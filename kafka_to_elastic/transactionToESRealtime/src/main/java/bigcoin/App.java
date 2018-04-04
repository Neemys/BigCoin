package bigcoin;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

import org.apache.spark.SparkConf;
import org.apache.spark.streaming.Durations;
import org.apache.spark.streaming.api.java.*;
import org.apache.spark.streaming.kafka010.*;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.elasticsearch.action.index.IndexResponse;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.transport.TransportAddress;
import org.elasticsearch.transport.client.PreBuiltTransportClient;
import org.elasticsearch.xpack.client.PreBuiltXPackTransportClient;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Base64;

/**
 * Spark Streaming from Kafka to ElasticSearch
 *
 */
public class App
{
    // Default config
    private static String broker = "localhost:9092";
    private static String topic = "transaction-realtime";
    private static String host_es = "localhost";
    private static Integer port_es = 9300;
    private static String currency = "EUR";

    public static void main( String[] args ) throws UnknownHostException {

        // Custom config (from input)
        if (args.length > 0) {
            host_es = args[0];
        }
        if (args.length > 1) {
            currency = args[1];
        }

        // Get user and password from system variable
        String es_user = System.getenv("ES_ADMIN_USER");
        String es_pwd = System.getenv("ES_ADMIN_PASSWORD");

        // Initialize Spark config and context
        SparkConf sparkConf = new SparkConf().setAppName("SparkStreamKafka").setMaster("local[2]");
        sparkConf.set("es.index.auto.create", "true");
        JavaStreamingContext streamingContext = new JavaStreamingContext(sparkConf, Durations.seconds(5));

        // Initialize Kafka DStream
        Map<String, Object> kafkaParams = new HashMap<>();
        kafkaParams.put("bootstrap.servers", broker);
        kafkaParams.put("key.deserializer", StringDeserializer.class);
        kafkaParams.put("value.deserializer", StringDeserializer.class);
        kafkaParams.put("group.id", "use_a_separate_group_id_for_each_stream");
        kafkaParams.put("auto.offset.reset", "latest");
        kafkaParams.put("enable.auto.commit", true);

        Collection<String> topics = Arrays.asList(topic);

        JavaInputDStream<ConsumerRecord<String, String>> stream =
                KafkaUtils.createDirectStream(
                        streamingContext,
                        LocationStrategies.PreferConsistent(),
                        ConsumerStrategies.<String, String>Subscribe(topics, kafkaParams)
                );

        // Format data from each RDD and insert into ES
        stream.foreachRDD(rdd -> {
            rdd.foreachPartition(partitionOfRecords -> {

                System.setProperty("es.set.netty.runtime.available.processors", "false");

                // Initialize ES client
                Settings settings = Settings.builder().put("xpack.security.user", es_user+":"+es_pwd).build();
                TransportClient client = new PreBuiltXPackTransportClient(settings)
                //TransportClient client = new PreBuiltTransportClient(Settings.EMPTY)
                        .addTransportAddress(new TransportAddress(InetAddress.getByName(host_es), port_es));

                DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMM dd, uuuu HH:mm:ss zzz", Locale.US);

                System.out.println("###########################  DEBUT DU MESSAGE  ###########################");

                while (partitionOfRecords.hasNext()) {

                    // Create a JSON from value of the record
                    JSONObject jsonObject = new JSONObject(partitionOfRecords.next().value());

                    jsonObject = jsonObject.getJSONObject("x");

                    Date date = new Date(jsonObject.getLong("time") * 1000);
                    long tx_index = jsonObject.getLong("tx_index");

                    // Get the sum of the inputs values
                    JSONArray jsonArray = jsonObject.getJSONArray("inputs");
                    long sumValue = 0;
                    for (int i = 0; i < jsonArray.length(); i++) {
                        jsonObject = jsonArray.getJSONObject(i);
                        sumValue += jsonObject.getJSONObject("prev_out").getLong("value");
                    }

                    Double doubleValue = (double)sumValue / 100000000;

                    // Create a liste of key/value
                    List<Object> values = new ArrayList();
                    values.add("date");
                    values.add(date);
                    values.add("value");
                    values.add(doubleValue);
                    values.add("data_type");
                    values.add("temps_reel");

                    // Insert data in ES
                    IndexResponse reponse = client.prepareIndex("transaction_idx", "transaction")
                            .setSource(values.toArray())
                            .get();

                    System.out.println("----------------------------------");
                    System.out.println(date);
                    System.out.println(sumValue);
                }
                System.out.println("###########################  FIN DU MESSAGE  ###########################");
                client.close();
            });

        });

        // Start Streaming
        streamingContext.start();
        try {
            streamingContext.awaitTermination();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
