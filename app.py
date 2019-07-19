# REQUIRED: Use MongoDB Compass to Open MongoDB

# Dependencies
from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo

# import scrape_mars function defined in scrape_mars.py
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish connection with mission_to_mars mongo db
mongo = PyMongo(app, uri="mongodb://localhost:27017/mission_to_mars")

@app.route("/")
def index():
    try:
        # find one record of data from the mongo database
        mars_data = mongo.db.mars_data.find_one()
        return render_template('index.html', mars_data=mars_data)
    except:
        return redirect("http://localhost:5000/scrape", code=302)


# route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function and execute the scrape method
    mars_data = mongo.db.mars_data
    mars_data_scrape = scrape_mars.scrape() #executing the method

    # Update the Mongo database using update and upsert=True
    # and update the index page with new information
    mars_data.update(
        {},
        mars_data_scrape,
        upsert=True
    )

    # Redirect back to index.html
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)

