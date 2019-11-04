import os
import requests


def gapi_get_response(address):
    global gapi_response
    gkey = os.getenv("GOOGLE_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={gkey}"
    gapi_response = requests.get(url)
    results = gapi_response.json()
    return results['status'] == 'OK'


def owapi_get_response(zipcode, country):
    global wapi_response
    # There is an open issue that doens't allow to search by zipcode from some places in other countries
    # https://openweathermap.desk.com/customer/portal/questions/17194531-search-by-zip-postal-code-not-working
    wkey = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?units=imperial&zip={zipcode},{country}&APPID={wkey}"
    wapi_response = requests.get(url)
    return "main" in wapi_response.json()


def gapi_get_postal_code():
    location = gapi_response.json()

    # default value (if no postal code is found)
    postal_code = False

    for result in location['results'][0]['address_components']:
        if result['types'][0] == 'postal_code':
            postal_code = result['long_name']

    return postal_code


def gapi_get_location_name():

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


def wapi_get_temperature():
    temperature = wapi_response.json()
    return temperature["main"]["temp"]
