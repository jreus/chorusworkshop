# inaudiblechorus

Setting up flask to broadcast locally: https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network

Run inside the given server directory with

```
export FLASK_APP=server.py && export FLASK_ENV=development && python -m flask run --host=0.0.0.0
``

Or make sure the host value is set to '0.0.0.0' when initializing the app in the server programme.

# TODO:

* stress test voice performance on local network / with local router
* stress test voice performance / synthesis with many simultaneous hits
