from app import app
from flask_sqlalchemy import SQLAlchemy
import os
import time

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
    country = db.Column(db.String(100))
    message = db.Column(db.String(250))

    def __init__(self, address, valid, last_request, zipcode, country, message):
        self.address = address
        self.valid = valid
        self.last_request = last_request
        self.zipcode = zipcode
        self.country = country
        self.message = message

    def __repr__(self):
        return '<User %r>' % self.address

    # get the most recent 10 searches given an string to filter
    @classmethod
    def query(cls, session, val):
        history = db.session.query(Searches).filter(Searches.address.ilike('%' + val + '%')).order_by(Searches.last_request.desc()).limit(10)
        result = []
        for h in history:
            result.append(h.address)
        return result

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


dbstatus = False
while dbstatus is False:
    try:
        db.create_all()
        db.session.commit()
    except Exception as e:

        time.sleep(2)
    else:
        dbstatus = True
