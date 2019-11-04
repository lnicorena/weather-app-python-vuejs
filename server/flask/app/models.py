
from app.database import DB

class Searches(DB.Model):
    address = DB.Column('address', DB.String(250), primary_key=True)
    valid = DB.Column(DB.Integer)
    last_request = DB.Column(DB.DateTime)
    zipcode = DB.Column(DB.String(15))
    country = DB.Column(DB.String(100))
    message = DB.Column(DB.String(250))

    def __init__(self, address, valid, last_request, zipcode, country, message):
        self.address = address
        self.valid = valid
        self.last_request = last_request
        self.zipcode = zipcode
        self.country = country
        self.message = message

    def __repr__(self):
        return '<Search addres={},  zipcode={}, country={}, valid={}, message={}>'.format(
            self.address, self.zipcode, self.country, self.valid, self.message)

    # get the most recent 10 searches given an string to filter
    @classmethod
    def query(cls, val):
        history = DB.session.query(Searches).filter(Searches.address.ilike(
            '%' + val + '%')).order_by(Searches.last_request.desc()).limit(10)
        result = []
        for h in history:
            result.append(h.address)
        return result


class Temperatures(DB.Model):
    zipcode = DB.Column('zipcode', DB.String(15), primary_key=True)
    value = DB.Column(DB.JSON)
    last_request = DB.Column(DB.DateTime)

    def __init__(self, zipcode, value, last_request):
        self.zipcode = zipcode
        self.value = value
        self.last_request = last_request

    def __repr__(self):
        return '<Temperature zipcode={}, last_request={}, temperature={}, location={}>'.format(
            self.zipcode, self.last_request, self.value['temperature'], self.value['location'])
            
