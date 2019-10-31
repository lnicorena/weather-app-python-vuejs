from app import app, db, Searches, Temperatures
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os


google_api_key = os.getenv("GOOGLE_API_KEY")
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# function to insert/update an object in the db
def db_persist(func):
    def persist(*args, **kwargs):
        func(*args, **kwargs)
        try:
            db.session.commit()
            # db.logger.info("success calling db func: " + func.__name__)
            return True
        except SQLAlchemyError as e:
            # db.logger.error(e.args)
            db.session.rollback()
            return False
        finally:
            db.session.close()
    return persist

@db_persist
def insert_or_update(table_object):
    return db.session.merge(table_object)
    # db.session.add(s)
    # db.session.commit()


# prepare the api response and save to db if so
# "status" codes:
#   -1 : error, log in the searches table on db
#   -2 : error
#    1 : success, log in the searches and temperatures table on db
def prepare_response(status, data, address, zipcode):
    
    if status < 0:
        if status == -1:
            s = Searches(address, 0, 'now()', zipcode, data)
            insert_or_update(s)

        return jsonify({
            'status': 'error',
            'errors': data
        })
    else:
        if status == 1:
            s = Searches(address, 1, 'now()', zipcode, "")
            insert_or_update(s)

            t = Temperatures(zipcode, data, 'now()')
            insert_or_update(t)

        return jsonify({
            'status': 'OK',
            'result': data
        })


# query in the searches history
@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')

    # query = db.select(Searches)
    result = Searches.query(db.session, q)

    return prepare_response(2, result, "", "")
    # return prepare_response(2, [
    #     '515 N. State Street',
    #     '459 Broadway'
    # ], "", "")


def get_googleapi_response(address):
    global gapi_response
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + \
        str(address) + "&key=" + google_api_key
    gapi_response = requests.get(url)

    results = gapi_response.json()
    # Error detected with the HTTP request or the Google API
    if(results['status'] != 'OK'):
        return(-1)
    else:
        return 0


def get_openweather_response(zipcode, country):
    global wapi_response
    # There is an open issue that doens't allow to search by zipcode from some places in other countries
    # https://openweathermap.desk.com/customer/portal/questions/17194531-search-by-zip-postal-code-not-working
    url = "http://api.openweathermap.org/data/2.5/weather?units=imperial&zip=" + \
        zipcode + "," + country + "&APPID=" + openweather_api_key

    wapi_response = requests.get(url)

    # @todo validate openweather request for errors
    if "main" in wapi_response.json():
        return 0
    else:
        return -1


def get_postal_code():
    location = gapi_response.json()

    # default value (if no postal code is found)
    postal_code = -1

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
        elif "administrative_area_level_2" in comp["types"] and city == False:
            city = comp["long_name"]
        elif "administrative_area_level_1" in comp["types"]:
            region = comp["short_name"]
        elif "country" in comp["types"]:
            country = comp["short_name"]

    return city, region, country


def get_temperature():
    temperature = wapi_response.json()
    return temperature["main"]["temp"]


@app.route('/temperature', methods=['GET'])
def temperature():
    address = request.args.get('address', "")

    if  address == "" :
        return prepare_response(-2, 'address param must be passed', "invalid", "")

    # load google api response
    gres = get_googleapi_response(address)
    if gres == -1:
        return prepare_response(-1, 'google api error', address, "")

    # get zip code
    zipcode = get_postal_code()
    if zipcode == -1:
        return prepare_response(-1, 'invalid address: zip code could not be found', address, zipcode)

    # get location details
    city, region, country = get_location_name()

    if not city or not region or not country:
        return prepare_response(-1, 'invalid address: location could not be found', address, zipcode)

    # load open weather api response
    wres = get_openweather_response(zipcode, country)
    if wres == -1:
        return prepare_response(-1, 'open weather api did not found the location to give the temperature', address, zipcode)

    # get current temperature
    temp = get_temperature()

    # return the temperature and location name
    results = {
        "temperature": temp,
        "location": city + ", " + region
    }
    return prepare_response(1, results, address, zipcode)

