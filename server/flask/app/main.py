from app import app
from app.database import db
from app.database import Searches
from app.database import Temperatures
from app import utils
from app.utils import prepare_response
from flask import jsonify
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# query in the searches history
@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    result = Searches.query(db.session, q)
    return prepare_response(utils.MSG_SUCCESS, result)


@app.route('/temperature', methods=['GET'])
def temperature():
    address = request.args.get('address', "")

    # error if param is not present
    if  address == "" :
        return prepare_response(utils.MSG_ERROR, 'address param must be passed', "invalid")
    
    ## check DATABASE for the ADDRESS
    history = db.session.query(Searches).filter(Searches.address.ilike(address)).first()

    ## if the address IS STORED on the DB
    if history:
        # check if is valid and get it!
        if history.valid == 1:
            zipcode = history.zipcode
            country = history.country

            temp = db.session.query(Temperatures).filter_by(zipcode=zipcode).first()

            location_name = temp.value['location']
            duration = utils.time_spent(temp.last_request)

            print('request cached on database. request age:' + str(duration))

            # if the temperature is newer than 1 hour, return it
            # else, git it from the weather api
            if duration < 60:
                response = make_response(prepare_response(utils.MSG_SUCCESS, temp.value), 200)
                response.headers['Cache-Control'] = "max-age={}".format(int(60 - duration) * 60)
                return response

        # otherwise return an error
        else: 
            return prepare_response(utils.MSG_ERROR_DB, history.message, address)
    

    ## The ADDRESS was NOT FOUND in the DB, get it from google API
    else:
        # load google api response
        gapi_requested = utils.get_googleapi_response(address)
        if not gapi_requested:
            return prepare_response(utils.MSG_ERROR, 'google api error', address)

        # get zip code
        zipcode = utils.get_postal_code()
        if not zipcode:
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: zip code could not be found', address, zipcode)

        # get location details
        city, region, country = utils.get_location_name()

        if not city or not region or not country:
            return prepare_response(utils.MSG_ERROR_DB, 'invalid address: location could not be found', address, zipcode, country)

        location_name = city + ", " + region



    ## If the Temperature was NOT FOUND in the database or is OLDER than 1 HOUR, get it from external API

    # load open weather api response
    wapi_requested = utils.get_openweather_response(zipcode, country)
    if not wapi_requested:
        return prepare_response(utils.MSG_ERROR_DB, 'open weather api did not found the location to give the temperature', address, zipcode, country)

    # GET current temperature
    temp = utils.get_temperature()

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

