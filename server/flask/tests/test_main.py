import unittest
import sys
import os
sys.path.append('../app')
from app import app
import json
from requests.utils import quote


class TestMainApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    # Test if application is running
    def test_root_status(self):
        response = self.app.get('/')
        self.assertEqual(200, response.status_code)

    def test_root_content_type(self):
        response = self.app.get('/')
        self.assertIn('application/json', response.content_type)

    def test_root_response(self):
        response = self.app.get('/')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, "It works!")

    # Test search endpoint

    def test_search_status(self):
        response = self.app.get('/search?q=test')
        self.assertEqual(200, response.status_code)

    def test_search_no_arguments(self):
        response = self.app.get('/search')
        expected = {
            'status': 'error',
            'errors': 'query param must be passed'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)

    def test_search_reponse(self):
        response = self.app.get('/search?q=something')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['status'], "OK")
        self.assertEqual(type(data['result']), type([]))

    # Test temperature endpoint

        

    def test_temperature_no_arguments(self):
        response = self.app.get('/temperature')
        expected = {
            'status': 'error',
            'errors': 'address param must be passed'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)
        self.assertEqual(400, response.status_code)

    def test_temperature_no_address_value(self):
        response = self.app.get('/temperature?address')
        expected = {
            'status': 'error',
            'errors': 'address param must be passed'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)
        self.assertEqual(400, response.status_code)

    def test_temperature_invalid_address_value(self):
        response = self.app.get(
            '/temperature?address=ABCDEFGH')
        expected = {
            'status': 'error',
            'errors': 'google api error'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)
        self.assertEqual(400, response.status_code)

    def test_temperature_nozipcode_address_value(self):
        response = self.app.get(
            '/temperature?address=Florianopolis')
        expected = {
            'status': 'error',
            'errors': 'invalid address: zipcode could not be found'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)
        self.assertEqual(400, response.status_code)

    def test_temperature_error_address_value(self):
        response = self.app.get(
            "/temperature?address=R. Dante de Patta, Ingleses, Florinópolis")
        expected = {
            'status': 'error',
            'errors': 'open weather api did not found the location to give the temperature'
        }
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data, expected)
        self.assertEqual(400, response.status_code)


    def test_temperature_response(self):
        response = self.app.get('/temperature?address={}'.format(quote('459 Broadway, New York')))
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['status'], "OK")
        self.assertEqual(200, response.status_code)
        
    def test_temperature_response_result(self):
        response = self.app.get('/temperature?address={}'.format(quote('459 Broadway, New York')))
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['result']['location'], 'New York, NY')
        self.assertIn(type(data['result']['temperature']), [type(70.0), type(70)],)
        self.assertEqual(200, response.status_code)
