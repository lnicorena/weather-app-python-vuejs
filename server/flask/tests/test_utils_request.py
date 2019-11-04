import unittest
import sys
sys.path.append('../app')
from app import app
from app.utils.request import prepare_response
from app.utils.request import MSG_ERROR
from app.utils.request import MSG_SUCCESS
import json


class TestUtilsRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_call_error_message(self):
        expected_message = "An error has occured"
        expected = {
            'status': 'error',
            'errors': expected_message
        }
        response = prepare_response(MSG_ERROR, expected_message)
        
        self.assertEqual(json.loads(response[0].get_data(as_text=True)), expected)

    def test_call_success_message(self):
        data_obj = {
            'status': '200',
            'message': 'Some success message'
        }
        expected = {
            'status': 'OK',
            'result': data_obj
        }
        response = prepare_response(MSG_SUCCESS, data_obj)
        
        self.assertEqual(json.loads(response[0].get_data(as_text=True)), expected)
