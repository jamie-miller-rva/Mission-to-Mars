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
        # print(mars_data)  used for troubleshooting
        return render_template('index.html', mars_data=mars_data) # fill in the {{ }} on the index.html file with the mars_data
    except:
        return redirect("http://localhost:5000/scrape", code=302) # if there is no data rediect to start scrape
        # print(e) used in troubleshooting

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


