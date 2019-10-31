from flask import Flask
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
import time


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@postgres/weatherdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'postgres'

db = SQLAlchemy(app)

class Searches(db.Model):
    address = db.Column('address', db.String(250), primary_key=True)
    valid = db.Column(db.Integer)
    last_request = db.Column(db.DateTime)
    zipcode = db.Column(db.String(15))
    message = db.Column(db.String(250))

    def __init__(self, address, valid, last_request, zipcode, message):
        self.address = address
        self.valid = valid
        self.last_request = last_request
        self.zipcode = zipcode
        self.message = message
    def __repr__(self):
        return '<User %r>' % self.address
    @classmethod
    def query(cls, session, val):
        records = session.query(cls).filter(Searches.address.like('%' + val + '%')).all()
        recordObjects = []
        for record in records:
            recordObjects.append(record.address)
            # recordObjects.append( {'address': record.address})
        return recordObjects

class Temperatures(db.Model):
    zipcode = db.Column('zipcode', db.String(15), primary_key=True)
    value = db.Column(db.JSON)
    last_request = db.Column(db.DateTime)

    def __init__(self, zipcode, value, last_request):
        self.zipcode = zipcode
        self.value = value
        self.last_request = last_request
    def __repr__(self):
        return '<User %r>' % self.zipcode

dbstatus = False
while dbstatus == False:
    try:
        db.create_all()
        db.session.commit()
    except Exception as e:

        time.sleep(2)
    else:
        dbstatus = True
    

from app import views
from app import main
