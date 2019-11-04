import unittest
import sys
sys.path.append('../app')
from app import app
from app.utils import external
import os
import requests
import responses
import json



class TestUtilsExternal(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.max_age = int(os.getenv("TEMPERATURE_MAX_AGE"))


    @responses.activate
    def test_gap_mock_response(self):
        # mock the google api response to a static json
        with open('tests/static/google_response.json', 'r') as f:
            gres = json.load(f)
        responses.add(responses.GET, 'https://maps.googleapis.com/maps/api/geocode/json', json=gres, status=200)
        
        # load the response
        resp = external.gapi_get_response('some address')

        self.assertTrue(resp)

        # get the zipcode
        zip = external.gapi_get_postal_code()
        self.assertEqual(zip, '10013')

        # get the location name
        expected_loc = 'New York', 'NY', 'US'
        zip = external.gapi_get_location_name()
        self.assertEqual(zip, expected_loc)


    # test the real response
    def test_gap_real_response(self):
        
        # load the response
        resp = external.gapi_get_response('459 Broadway, New York')

        self.assertTrue(resp)

        # get the zipcode
        zip = external.gapi_get_postal_code()
        self.assertEqual(zip, '10013')

        # get the location name
        expected_loc = 'New York', 'NY', 'US'
        zip = external.gapi_get_location_name()
        self.assertEqual(zip, expected_loc)
        
        
    @responses.activate
    def test_wap_mock_response(self):
        # mock the google api response to a static json
        with open('tests/static/weather_response.json', 'r') as f:
            wres = json.load(f)
        responses.add(
            responses.GET, 'http://api.openweathermap.org/data/2.5/weather', json=wres, status=200)

        # load the response
        resp = external.wapi_get_response('10013', 'US')

        self.assertTrue(resp)

        # get the temperature
        temperature = external.wapi_get_temperature()
        self.assertEqual(temperature, 35.24)
