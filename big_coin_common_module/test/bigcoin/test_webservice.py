
try:
    # Python 3
    from unittest import mock
except ImportError:
    # Python 2, install from pip first
    import mock
import unittest
from bigcoin import webservice
import json
import requests

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://mock.url/test1':
        return MockResponse({"key1": "value1"}, 200)
    if args[0] == 'http://mock.url/timeout':
        raise requests.exceptions.Timeout()

    return MockResponse(None, 404)


class TestWebservice(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_json_from_address(self, mock_get):
        #test normal response
    	response = webservice.get_json_from_address("http://mock.url/test1")
    	self.assertEqual(response, {"key1": "value1"})
        #test exit with error 20 on non ok response
        passed_404 = False
        try:
            response = webservice.get_json_from_address("http://mock.url/inexistant_url")
        except SystemExit as e:
            if e.code == 20:
                passed_404 = True
        assert passed_404
        #test exit with error 10 on timeout
        passed_timeout = False
        try:
            response = webservice.get_json_from_address("http://mock.url/timeout")
        except SystemExit as e:
            if e.code == 10:
                passed_timeout = True
        assert passed_timeout
if __name__ == "__main__":
    unittest.main()
