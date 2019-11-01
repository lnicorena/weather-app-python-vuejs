from app import app
import os
import requests
from datetime import datetime
from app.database import Searches
from app.database import Temperatures
from app.database import insert_or_update
from flask import jsonify


def get_googleapi_response(address):
    global gapi_response
    gkey = os.getenv("GOOGLE_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={gkey}"
    gapi_response = requests.get(url)
    results = gapi_response.json()
    return results['status'] == 'OK'


def get_openweather_response(zipcode, country):
    global wapi_response
    # There is an open issue that doens't allow to search by zipcode from some places in other countries
    # https://openweathermap.desk.com/customer/portal/questions/17194531-search-by-zip-postal-code-not-working
    wkey = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?units=imperial&zip={zipcode},{country}&APPID={wkey}"
    wapi_response = requests.get(url)
    return "main" in wapi_response.json()


def get_postal_code():
    location = gapi_response.json()

    # default value (if no postal code is found)
    postal_code = False

    for result in location['results'][0]['address_components']:
        if result['types'][0] == 'postal_code':
            postal_code = result['long_name']

    return postal_code


def get_location_name():

    location = gapi_response.json()

    country = False
    region = False
    city = False
    components = location["results"][0]["address_components"]
    for comp in components:
        if "locality" in comp["types"]:
            city = comp["long_name"]
        elif "administrative_area_level_2" in comp["types"] and city is False:
            city = comp["long_name"]
        elif "administrative_area_level_1" in comp["types"]:
            region = comp["short_name"]
        elif "country" in comp["types"]:
            country = comp["short_name"]

    return city, region, country


def get_temperature():
    temperature = wapi_response.json()
    return temperature["main"]["temp"]


# calculate the amount of minutes between a given timestamp and now()
def time_spent(start_time):
    current_time = datetime.utcnow()
    duration = current_time - start_time
    minutes = divmod(duration.total_seconds(), 60)
    return minutes[0]



# Prepare a json with an error message
MSG_ERROR = -1
# Same as MSG_ERROR and also log the error on database (to be used as a cache)
MSG_ERROR_DB = -2
# Prepare a json with an success message
MSG_SUCCESS = 1
# Same as MSG_SUCCESS and save the result to the database for caching
MSG_SUCCESS_DB = 2

# prepare the api response and save to db if so


def prepare_response(status, data, address="", zipcode="", country=""):

    if status is MSG_ERROR_DB:
        # Save the invalid search to the DB so we don't search it again
        s = Searches(address, 0, 'now()', zipcode, country, data)
        insert_or_update(s)

    if status is MSG_SUCCESS_DB:
        # Searches is used to get the historic of places the user have searched
        s = Searches(address, 1, 'now()', zipcode, country, "")
        insert_or_update(s)

        # Temperatures is used for caching the temperature into database
        t = Temperatures(zipcode, data, 'now()')
        insert_or_update(t)

    result = {}

    if status in [MSG_SUCCESS, MSG_SUCCESS_DB]:
        result['status'] = 'OK'
        result['result'] = data

    if status in [MSG_ERROR, MSG_ERROR_DB]:
        result['status'] = 'error'
        result['errors'] = data

    return jsonify(result)
