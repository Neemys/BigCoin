
try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2, install from pip first
    import mock
import unittest
from kafka import KafkaProducer
import kafka
from kafka.errors import KafkaTimeoutError
from bigcoin import bc_kafka
import collections

#Generator used to send values to the tested method
def generator_kafka_data(obj):
    for value in obj:
        yield value['message'],value['key'],value['timestamp_ms']



class TestBCKafkaProducer(unittest.TestCase):

    @mock.patch.object(KafkaProducer,'__init__') #Need to test if constructor called once, no init problem since the instance is created in __new__
    @mock.patch.object(KafkaProducer,'send')
    def test_send_to_topic_from_generator(self, mock_send, mock_init):
        #Necessary as constructor don't return anything and mock return the mock by default
        mock_init.return_value = None

        #Test normal behavior
        topic = "mock_topic"
        client_id = "mock_client_id"
        json = [
            {"message":"mess","key":"key","timestamp_ms":"1000000"},
            {"message":"mess2","key":None,"timestamp_ms":"1000000"},
            {"message":"mess3","key":"key","timestamp_ms":None},
            {"message":None,"key":None,"timestamp_ms":None},
        ]
        bc_kafka.send_to_topic_from_generator(topic,client_id,generator_kafka_data(json))

        calls = [mock.call(value=x['message'],key=x['key'],timestamp_ms=x['timestamp_ms'],topic=topic) for x in json]

        mock_init.assert_called_once()
        mock_send.assert_has_calls(calls)

        #Test when kafka timeout
        mock_send.side_effect = KafkaTimeoutError()
        passed_timeout = False
        try:
            bc_kafka.send_to_topic_from_generator(topic,client_id,generator_kafka_data(json))
        except SystemExit as e:
            if e.code == 30:
                passed_timeout = True
        assert passed_timeout

#By wrapping all test function we want to check that only one KafkaConsumer is ever created
def assert_one_init (fn):
    def wrapper(arg):
        fn(arg)
        arg._mock_consumer.assert_called_once()
    return wrapper

class TestBCKafkaConsumer(unittest.TestCase):

    #Store instance of tested object
    _bckafka_consumer = None
    _mock_consumer = None
    _mock_consumer_instance = None

    def setUp(self):
        #To be able to mock __init__ and all methods, we need to create two mock :
        # one for the class (will test that one instance is created)
        # the other will be the instance our object will use (mock methods)
        self.patcher = mock.patch("kafka.KafkaConsumer")
        self._mock_consumer = self.patcher.start()
        self._mock_consumer_instance = mock.MagicMock()
        self._mock_consumer.return_value = self._mock_consumer_instance
        self._bckafka_consumer = bc_kafka.BCKafkaConsumer("mock_topic","mock_client_id")

    @assert_one_init
    def tearDown(self):
        self.patcher.stop()

    @assert_one_init
    def test_get_messages(self):
        mock_poll = self._mock_consumer_instance.poll
        BCTestRecord = collections.namedtuple('BCTestRecord','value shouldn_appear')
        #test normal message
        expected_messages = ['["test":"test"]',
            '["test2":"test2"]',
            '["other_json":{"test3":"test3","test4":"tata"}]',
        ]
        mock_poll.return_value = {
            'partition1': [
                BCTestRecord(value=expected_messages[0],shouldn_appear='["shouldn_appear":"shouldnappear"]')
            ],
            'partition2': [
                BCTestRecord(value=expected_messages[1],shouldn_appear=None),
                BCTestRecord(value=expected_messages[2],shouldn_appear='["shouldn_appear_again":"shouldnappear"]')
            ]
        }

        messages = self._bckafka_consumer.get_messages()
        mock_poll.assert_called_once()
        self.assertListEqual(messages,expected_messages)

        mock_poll.reset_mock()

        #Test empty response
        mock_poll.return_value = {
            'partition1': [],
            'partition2': []
        }
        expected_messages = []
        messages = self._bckafka_consumer.get_messages()
        mock_poll.assert_called_once()
        self.assertListEqual(messages,expected_messages)


    @assert_one_init
    def test_set_messages_read(self):
        mock_commit = self._mock_consumer_instance.commit
        self._bckafka_consumer.set_messages_read()
        mock_commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
