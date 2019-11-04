from .. import app
from app.database import Searches
from app.database import Temperatures
from app.database import insert_or_update
from flask import jsonify



# Prepare a json with an error message
MSG_ERROR = -1
# Same as MSG_ERROR and also log the error on database (to be used as a cache)
MSG_ERROR_DB = -2
# Prepare a json with an success message
MSG_SUCCESS = 1
# Same as MSG_SUCCESS and save the result to the database for caching
MSG_SUCCESS_DB = 2

# prepare the api response and save to DB if so


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
