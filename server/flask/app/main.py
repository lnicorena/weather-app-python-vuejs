from app import app
from app import cache
from app.database import Searches
from app.utils.request import prepare_response
from app.utils import request as utils
from app.utils import external as API
from app.utils.caching import get_temperature_ttl
from app.utils.caching import get_search_history
from app.utils.caching import load_information_from_database
from flask import jsonify
from flask import request
from flask import make_response
import requests
import os
from datetime import datetime


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



@app.route('/temperature', methods=['GET'])
def temperature():
    address = request.args.get('address', False)

    # error if param is not present
    if not address:
        return prepare_response(utils.MSG_ERROR, 'address param must be passed')

    # if the address is in cache, get the temperature from there 
    if cache.get(address) is not None:
        print ("request cached from redis")
        return prepare_response(utils.MSG_SUCCESS, cache.get(address))
        
    TEMPERATURE_MAX_AGE = int(os.getenv("TEMPERATURE_MAX_AGE"))

    ## check DATABASE's search history for the given ADDRESS
    history = get_search_history(address)

    ## if there is an address STORED on the DB
    if history:
        # It should be valid so we can use
        if history.valid == 1:

            # get the temperature's info from database
            zipcode, country, location_name, last_request, temperature_value = load_information_from_database(history)
            
            # get the time that the temperature has to still be valid
            temperature_ttl = get_temperature_ttl(last_request)

            # return the stored temperature if it is still valid. Otherwise, get from the weather API
            if temperature_ttl > 0:
                response = make_response(prepare_response(
                    utils.MSG_SUCCESS, temperature_value)[0], 200)
                # set http caching with the remaining time of the temperature stored
                response.headers['Cache-Control'] = "max-age={}".format(temperature_ttl)
                print('request cached from database. remaining time (seconds): {}'.format(temperature_ttl))


                # set response in redis cache with the remaining time as max-age too
                cache.set(address, temperature_value, timeout=temperature_ttl)

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
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: zipcode could not be found', address, zipcode)

        # get location details
        city, region, country = API.gapi_get_location_name()

        if not city or not region or not country:
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: location could not be found', address, zipcode, country)

        location_name = city + ", " + region



    ## If the Temperature was NOT FOUND in the database or is OLDER than 1 HOUR, get it from external API

    # load open weather api response
    wapi_requested = API.wapi_get_response(zipcode, country)
    if not wapi_requested:
        return prepare_response(utils.MSG_ERROR_DB, 'open weather api did not found the location to give the temperature', address, zipcode, country)

    # GET current temperature
    temp = API.wapi_get_temperature()

    # temperature value and location name to return
    results = {
        "temperature": temp,
        "location": location_name
    }
    
    # set the temperature in redis cache, in case of another client calls for the same address
    cache.set(address, results, timeout=TEMPERATURE_MAX_AGE)

    # prepare the response and store it on the DB 
    response = make_response(prepare_response(utils.MSG_SUCCESS_DB, results, address, zipcode, country)[0], 200)

    # also set the http cache to 1 hour
    response.headers['Cache-Control'] = "max-age={}".format(
        TEMPERATURE_MAX_AGE)

    return response

