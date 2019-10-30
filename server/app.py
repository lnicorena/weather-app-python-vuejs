from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# change to environment variable?
google_api_key = 'AIzaSyBe5NnvWyecZfVzrXV0XfgGQG0uRATuYfQ'
openweather_api_key = '5461b7b4581b49127f32fe95aa5519d2'

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


def prepare_response(success, data):
    if success:
        return jsonify({
            'status': 'OK',
            'result': data
        })
    else:
        return jsonify({
            'status': 'error',
            'errors': data
        })

# query in the searches history
@app.route('/search', methods=['GET'])
def search():
    # q = request.args.get('q')

    return prepare_response(True, [
        '515 N. State Street',
        '459 Broadway'
    ])


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
    address = request.args.get('address')

    # load google api response
    gres = get_googleapi_response(address)
    if gres == -1:
        return prepare_response(False, 'google api error')

    # get zip code
    zipcode = get_postal_code()
    if zipcode == -1:
        return prepare_response(False, 'invalid address: zip code could not be found')

    # get location details
    city, region, country = get_location_name()

    if not city or not region or not country:
        return prepare_response(False, 'invalid address: location could not be found')

    # load open weather api response
    wres = get_openweather_response(zipcode, country)
    if wres == -1:
        return prepare_response(False, 'open weather api did not found the location to give the temperature')

    # get current temperature
    temp = get_temperature()

    # return the temperature and location name
    results = {
        "temperature": temp,
        "location": city + ", " + region
    }
    return prepare_response(True, results)


if __name__ == '__main__':
    app.run()
