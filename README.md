# Weather app 
Vue.js SPA served over Flask microframework

* Python: 3.8.0
* Vue.js: 2.6.10
* vue-router: 3.0.6
* axios: 0.19.0


## Front-end setup

``` bash

cd client

# Rename the .env file
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
cd server

# Create python virtual env 
virtualenv -p python venv

# Activate virtual env
source venv/bin/activate

# Install project requirements
pip install -r requirements.txt

# serve back-end at localhost:5000
FLASK_APP=app.py flask run

```
