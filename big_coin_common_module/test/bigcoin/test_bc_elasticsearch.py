
try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2, install from pip first
    import mock
import unittest
import elasticsearch
from bigcoin import bc_elasticsearch

def send_once_none_generator():
    yield None

#By wrapping all test function we want to check that only one Elasticsearch is ever created
def assert_one_init (fn):
    def wrapper(*args, **kwargs):
        fn(*args, **kwargs)
        args[0]._mock_es.assert_called_once()
    return wrapper

class TestBCElasticsearch(unittest.TestCase):

    #Store instance of tested object
    _bces_es = None
    _mock_es = None
    _mock_es_instance = None

    def setUp(self):
        self._patcher = mock.patch("elasticsearch.Elasticsearch")
        self._mock_es = self._patcher.start()
        self._mock_es_instance = mock.Mock()
        self._mock_es.return_value = self._mock_es_instance
        self._bces_es = bc_elasticsearch.BCElasticsearch()

    @assert_one_init
    def tearDown(self):
        self._patcher.stop()

    @assert_one_init
    @mock.patch("elasticsearch.helpers.bulk")
    def test_send_messages(self,mock_bulk):
        #test normal behavior
        generator = send_once_none_generator()
        self._bces_es.send_messages(generator)
        mock_bulk.assert_called_once()
        mock_bulk.assert_called_with(self._mock_es_instance,generator)
        #test should exit(50) on timeout
        mock_bulk.side_effect = elasticsearch.ConnectionTimeout()
        with self.assertRaises(SystemExit) as cm:
            self._bces_es.send_messages(generator)
        self.assertEqual(cm.exception.code,50)

if __name__ == "__main__":
    unittest.main()
