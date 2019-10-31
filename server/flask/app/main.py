from app import app
from app.database import db, Searches, Temperatures
from flask import jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            return False
        finally:
            db.session.close()
    return persist

@db_persist
def insert_or_update(table_object):
    return db.session.merge(table_object)


# prepare the api response and save to db if so
# "status" codes:
#   -1 : error, log in the searches table on db
#   -2 : error
#    1 : success, log in the searches and temperatures table on db
#    2 : success, do not save to db
def prepare_response(status, data, address="", zipcode="", country=""):
    
    if status < 0:
        if status == -1:
            s = Searches(address, 0, 'now()', zipcode, country, data)
            insert_or_update(s)

        return jsonify({
            'status': 'error',
            'errors': data
        })
    else:
        if status == 1:
            s = Searches(address, 1, 'now()', zipcode, country, "")
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
    result = Searches.query(db.session, q)
    return prepare_response(2, result)


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

def time_spent(start_time):
    current_time = datetime.utcnow()
    duration = current_time - start_time
    minutes = divmod(duration.total_seconds(), 60)
    return minutes[0]

@app.route('/temperature', methods=['GET'])
def temperature():
    address = request.args.get('address', "")

    # error if param is not present
    if  address == "" :
        return prepare_response(-2, 'address param must be passed', "invalid")
    
    ## check database for the ADDRESS
    history = db.session.query(Searches).filter(Searches.address.ilike(address)).first()

    ## if the address is stored on the database
    if not history is None:
        # check if is valid and get it!
        if history.valid == 1:
            zipcode = history.zipcode
            country = history.country

            temp = db.session.query(Temperatures).filter_by(zipcode=zipcode).first()

            location_name = temp.value['location']
            duration = time_spent(temp.last_request)

            print('request cached on database. request age:' + str(duration))
            

            # if the temperature is newer than 1 hour, return it
            # else, git it from the weather api
            if (duration < 60):
                response = make_response(prepare_response(2, temp.value), 200)
                response.headers['Cache-Control'] = "max-age={}".format(int(60 - duration) * 60)
                return response

        # otherwise return an error
        else: 
            return prepare_response(-1, history.message, address)
    

    ## The address was not found in the database, get it from google api
    else:
        # load google api response
        gres = get_googleapi_response(address)
        if gres == -1:
            return prepare_response(-1, 'google api error', address)

        # get zip code
        zipcode = get_postal_code()
        if zipcode == -1:
            return prepare_response(-1, 'invalid address: zip code could not be found', address, zipcode)

        # get location details
        city, region, country = get_location_name()

        if not city or not region or not country:
            return prepare_response(-1, 'invalid address: location could not be found', address, zipcode, country)

        location_name = city + ", " + region



    ## If the temperature was not found in the database or is older than 1 hour, get it from external api

    # load open weather api response
    wres = get_openweather_response(zipcode, country)
    if wres == -1:
        return prepare_response(-1, 'open weather api did not found the location to give the temperature', address, zipcode, country)

    # get current temperature
    temp = get_temperature()

    # return the temperature and location name
    results = {
        "temperature": temp,
        "location": location_name
    }

    response = make_response(prepare_response(1, results, address, zipcode, country), 200)
    response.headers['Cache-Control'] = "max-age=3600"

    return response

