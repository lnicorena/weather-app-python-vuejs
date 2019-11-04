from .. import app
from app.database import DB
from app.database import Searches
from app.database import Temperatures
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


def get_search_history(address):
    return DB.session.query(Searches).filter(Searches.address.ilike(address)).first()


def load_information_from_database(search_history_obj):
    zipcode = search_history_obj.zipcode
    country = search_history_obj.country

    temp = DB.session.query(Temperatures).filter_by(zipcode=zipcode).first()

    location_name = temp.value['location']
    last_request = temp.last_request
    temperature_value = temp.value

    return zipcode, country, location_name, last_request, temperature_value
