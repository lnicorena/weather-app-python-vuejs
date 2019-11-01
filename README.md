# Weather app 

### Vue.js SPA served over Flask and PostgreSQL

Users can input an address and get the current temperature

## Features

### Temperature are searched by zipcode
    
Searches are cached on the DB so the server doesn't need to go again at the external API for the same address.
    
### The history of searches is showed to the user

The app is loaded with the last 10 searches. As the user types the app shows the matched searches and, when user stops typing, the app reload the searches (suggestions) with the most recent 10 search that matches the address user have typed.

### The temperature is stored on the DB

We assumed that a temperature picked on the external API is valid for one hour. So we store this temperature on the database and if it is still valid we dont need to go at the external API again.

### HTTP caching for temperature requests

As we defined that a temperature is valid for 1 hour, the request that gets a temperature is given by our server with a max-age equals the remaining time the temperature has to still be valid. So the brower don't ask the server again until it is needed.

### External APIs

The application access `Google Geocoding` API and `Open Weather Map’s API` to get address and current temperature.

### Testing

We have unit tests on the back-end and on the front-end. The front-end also have integration tests.

### Instructions 

Follow the above instructions to get the app running.

## Front-end setup

``` bash

cd client

# Rename the .env file and configure the API address and port
mv .env-example .env

# Install project dependencies
yarn install

# Compiles and hot-reloads for development at localhost:8080
yarn serve

# Compiles and minifies for production
yarn build

# Run front-end tests
yarn test:unit
yarn test:e2e
```

## Back-end setup

``` bash

# using docker-compose (recommended)

cd server

# build and run the containers (api will be available at: http://127.0.0.1:8081)
docker-compose up --build

# run tests
docker exec -it flask py.test



# or you can start the app manually

cd server/flask

# Create python virtual env 
virtualenv -p python venv

# Activate virtual env
source venv/bin/activate

# Install project requirements
pip install -r requirements.txt

# serve back-end at localhost:5000
FLASK_APP=app.py flask run

# Compiles and hot-reloads for development at localhost:5000
FLASK_APP=app.py FLASK_DEBUG=1 python -m flask run

# update/save requirements
pip freeze > requirements.txt

# run tests
py.test

```
