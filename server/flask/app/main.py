from app import app
from app.database import DB
from app.database import Searches
from app.database import Temperatures
from app.utils.request import prepare_response
from app.utils import request as utils
from app.utils import external as API
from app.utils.caching import get_temperature_ttl
from flask import jsonify
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
import requests
import os


# sanity check route
@app.route('/', methods=['GET'])
def ping_pong():
    return jsonify('It works!')


# query in the searches history
@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q', False)
    if q is False:
        return prepare_response(utils.MSG_ERROR, 'query param must be passed')

    result = Searches.query(q)
    return prepare_response(utils.MSG_SUCCESS, result)


def _get_search_history (address):
    return DB.session.query(Searches).filter(Searches.address.ilike(address)).first()

def _load_information_from_database(search_history_obj):
    zipcode = search_history_obj.zipcode
    country = search_history_obj.country

    print(search_history_obj)
    temp = DB.session.query(Temperatures).filter_by(zipcode=zipcode).first()
    print (temp)
    location_name = temp.value['location']
    last_request = temp.last_request
    temperature_value = temp.value

    return zipcode, country, location_name, last_request, temperature_value



@app.route('/temperature', methods=['GET'])
def temperature():
    address = request.args.get('address', False)

    # error if param is not present
    if not address:
        return prepare_response(utils.MSG_ERROR, 'address param must be passed')
    
    ## check DATABASE's search history for the given ADDRESS
    history = _get_search_history(address)

    ## if there is an address STORED on the DB
    if history:
        # It should be valid so we can use
        if history.valid == 1:

            # get the temperature's info from database
            zipcode, country, location_name, last_request, temperature_value = _load_information_from_database(
                history)
            
            # get the time that the temperature has to still be valid
            temperature_ttl = get_temperature_ttl(last_request)

            # return the stored temperature if it is still valid. Otherwise, get from the weather API
            if temperature_ttl > 0:
                response = make_response(prepare_response(
                    utils.MSG_SUCCESS, temperature_value), 200)
                # set http caching with the remaining time of the temperature stored
                response.headers['Cache-Control'] = "max-age={}".format(temperature_ttl)
                print('request cached from database. remaining time (seconds): {}'.format(temperature_ttl))
                return response

        # otherwise return an error
        else: 
            return prepare_response(utils.MSG_ERROR_DB, history.message, address)
    

    ## The ADDRESS was NOT FOUND in the DB, get it from google API
    else:
        # load google api response
        gapi_requested = API.gapi_get_response(address)
        if not gapi_requested:
            return prepare_response(utils.MSG_ERROR, 'google api error', address)

        # get zip code
        zipcode = API.gapi_get_postal_code()
        if not zipcode:
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: zip code could not be found', address, zipcode)

        # get location details
        city, region, country = API.gapi_get_location_name()

        if not city or not region or not country:
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: location could not be found', address, zipcode, country)

        location_name = city + ", " + region



    ## If the Temperature was NOT FOUND in the database or is OLDER than 1 HOUR, get it from external API

    # load open weather api response
    wapi_requested = API.owapi_get_response(zipcode, country)
    if not wapi_requested:
        return prepare_response(utils.MSG_ERROR_DB, 'open weather api did not found the location to give the temperature', address, zipcode, country)

    # GET current temperature
    temp = API.wapi_get_temperature()

    # temperature value and location name to return
    results = {
        "temperature": temp,
        "location": location_name
    }

    # prepare the response and store it on the DB 
    response = make_response(prepare_response(utils.MSG_SUCCESS_DB, results, address, zipcode, country), 200)

    # also set the http cache to 1 hour
    response.headers['Cache-Control'] = "max-age=3600"

    return response

