from .. import app
from datetime import datetime
import os

# calculate the amount of seconds between a given timestamp and now()
def _time_spent(start_time):
    current_time = datetime.utcnow()
    duration = current_time - start_time
    return duration.total_seconds()

# returns the remaining time a stored temperature still has to be used 
def get_temperature_ttl(last_request_time=0):
    temperature_ttl = int(os.getenv("TEMPERATURE_MAX_AGE"))
    spent_time = int(_time_spent(last_request_time)) if last_request_time else 0
    return temperature_ttl - spent_time

