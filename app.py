# REQUIRED: Use MongoDB Compass to Open MongoDB

# Dependencies
from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import pymongo
import scrape_mars # import scrape_mars function defined in scrape_mars.py

# Create an instance of Flask
app = Flask(__name__)

# Establish PyMongo connection with mission_to_mars mongo db
mongo = PyMongo(app, uri="mongodb://localhost:27017/mission_to_mars")

@app.route("/")
def index():
    try:
        # find one record of data from the mission_to_mars database collection called mars_data
        mars_data = mongo.db.mars_data.find_one()
        return render_template('index.html', mars_data=mars_data) # fill in the {{ }} on the index.html file with the mars_data
    except:
        return redirect("http://localhost:5000/scrape", code=302) # if there is no data rediect to start scrape

# route that will trigger the scrape function
@app.route("/scrape")
def scraped(): 
    mars_data = mongo.db.mars_data
    mars_data_scrape = scrape_mars.scrape() #executing the method

    # Update the mission_to_mars database: update and insert data into the db collection mars_data using upsert=True
    mars_data.update(
        {},
        mars_data_scrape,
        upsert=True # upsert is a combination of update and insert
    )
    # Redirect back to index.html
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)

# Current Issue is code is running in a loop where it does not get a 
# 127.0.0.1 - - [21/Jul/2019 09:46:22] "GET / HTTP/1.1" 200 -
# but instead gets 127.0.0.1 - - [21/Jul/2019 10:50:52] "GET / HTTP/1.1" 302 -
# which puts it into a loop
# Note code 302 is:
# The requested resource resides temporarily under a different URI. 
# Since the redirection might be altered on occasion, 
# the client SHOULD continue to use the Request-URI for future requests. 
# This response is only cacheable if indicated by a Cache-Control or Expires header field.
# The temporary URI SHOULD be given by the Location field in the response. 
# Unless the request method was HEAD, the entity of the response SHOULD contain
# a short hypertext note with a hyperlink to the new URI(s).
# If the 302 status code is received in response to a request other than GET or HEAD,
# the user agent MUST NOT automatically redirect the request 
# unless it can be confirmed by the user, since this might change the conditions
# under which the request was issued.

