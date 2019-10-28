# Weather app 
Vue.js SPA served over Flask microframework

* Python: 3.8.0
* Vue.js: 2.6.10
* vue-router: 3.0.6
* axios: 0.19.0


## Build Setup

``` bash
# install front-end
cd client
yarn install

# serve with hot reload at localhost:8080
yarn serve

# build for production/Flask with minification
yarn build


# install back-end
cd ../server
virtualenv -p python venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# serve back-end at localhost:5000
FLASK_APP=app.py flask run
```
