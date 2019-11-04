import unittest
import sys
sys.path.append('../app')
from app import app
from app.utils.caching import get_temperature_ttl
import os
from datetime import datetime
from datetime import timedelta



class TestUtilsCaching(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.max_age = int(os.getenv("TEMPERATURE_MAX_AGE"))

    # Time returned should be equal the max age 
    def test_call_temperature_ttl_with_no_params(self):
        self.assertEqual(self.max_age, get_temperature_ttl())
        
    # 15 minutes ago time should return max age - 15 minutes
    def test_call_temperature_ttl_minutes_ago(self):
        time = datetime.utcnow() - timedelta(minutes=15)
        ttl = get_temperature_ttl(time)
        self.assertEqual(ttl, self.max_age - 15*60)

    # max-aged time should return negative value
    def test_call_temperature_ttl_minutes_old(self):
        total = int (self.max_age / 60) + 15
        time = datetime.utcnow() - timedelta(minutes=total)
        ttl = get_temperature_ttl(time)
        self.assertLess(ttl, 0)
