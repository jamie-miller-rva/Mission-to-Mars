# Dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd
from time import sleep

def init_browser():
    """ Sets a path to the browser (chrome) and identifies the location of the chromedriver"""

    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False) # False to see the browser open

def scrape():
    """
    Scrape the following websites for Mars data:
    NASA Mars News Site, 
    NASA Jet Propulsion Laboratory site, 
    Mars Weather twitter account, Mars Facts Web page 
    USGS Astrogeology site 
    """

    # Establish a dictionary to store scraped Mars information
    Mars_info_dict = {}

    #--------------------------------------------------------------
    #-- Scrape the NASA Mars News Site
    #--------------------------------------------------------------
    
    # Use requests and Beautifulsoup to scarpe NASA Mars News Site
    NASA_url = "https://mars.nasa.gov/news/"
    # Retrieve page with the requests module
    NASA_html = requests.get(NASA_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    NASA_soup = bs(NASA_html.text, 'html.parser')

    # Get news title & paragraph description
    news_title = NASA_soup.find('div', 'content_title', 'a').get_text().strip()
    news_paragraph = NASA_soup.find('div', 'rollover_description_inner').get_text().strip()

    # Add the title and description to the dictionary
    Mars_info_dict["news_title"] = news_title
    Mars_info_dict["news_paragraph"] = news_paragraph

    #--------------------------------------------------------------
    #-- Scrape the NASA Jet Propulsion Laboratory site
    #--------------------------------------------------------------
    
    # Open the JPL url using Chrome
    JPL_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(JPL_url) # opens up the JPL website

    JPL_html=browser.html # take out the information in html format
    JPL_soup = bs(JPL_html, 'html.parser')

    # Get the featured item
    featured = JPL_soup.find('div', class_='default floating_text_area ms-layer')
    featured_image = featured.find('footer')
    featured_image_url = 'https://www.jpl.nasa.gov/' + featured_image.find('a')['data-fancybox-href']

    # Add featured item to dictionary
    Mars_info_dict['featured_image'] = JPL_soup.find('div', class_='default floating_text_area ms-layer')
    Mars_info_dict['featured_image_url'] = 'https://www.jpl.nasa.gov/' + featured_image.find('a')['data-fancybox-href']

    #--------------------------------------------------------------
    #-- Scrape the Mars Weather twitter account
    #--------------------------------------------------------------
    
    mars_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    mars_twitter_response = requests.get(mars_twitter_url)

    # Retrieve 'mars_weather'
    mars_twitter_soup = bs(mars_twitter_response.text, 'html.parser')
    mars_twitter_result = mars_twitter_soup.find('div', class_='js-tweet-text-container')

    # Assign the scraped text to a variable 'mars_weather'
    mars_weather = mars_twitter_result.find('p', class_='js-tweet-text').text
    mars_weather

    # Store scraped data in dictionary
    Mars_info_dict['mars_weather'] = mars_weather

    #--------------------------------------------------------------
    #-- Scrape the Mars Facts Web page
    #--------------------------------------------------------------

    # Mars Facts Table
    mars_facts_url = 'https://space-facts.com/mars/'
    mars_facts_table = pd.read_html(mars_facts_url, index_col=0, flavor=['lxml', 'bs4'])
    mars_facts_table

    # Create pandas DataFrame for first table "Mars- Earth Comparison"
    Mars_Earth_Comparison_df = mars_facts_table[0]
    Mars_Earth_Comparison_df.columns = ['Mars', 'Earth']
    Mars_Earth_Comparison_df

    #Convert the data to a HTML table string.
    Mars_facts = Mars_Earth_Comparison_df.to_html()
    Mars_facts.replace("\n", "")
    Mars_Earth_Comparison_df.to_html('Output/mars_facts.html')

    # Store html file in dictionary
    Mars_info_dict['mars_facts'] = mars_facts

    #--------------------------------------------------------------
    #-- Scrape the USGS Astrogeology site
    #--------------------------------------------------------------

    # Open the USGS url using Chrome
    USGS_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(USGS_url)

    # Retrieve the image string in html formate for the full resolution hemisphere image, and the Hemisphere title containing the hemisphere name
    USGS_html = browser.html
    USGS_soup = bs(USGS_html, 'html.parser')

    USGS_image_list = USGS_soup.find_all('div', class_='item')

    # Create a list called hemisphere_title_and_image
    hemispheres_title_and_image = []

    base_url ="https://astrogeology.usgs.gov" # neeed below

    # Loop through each hemisphere and click on the link to find the large resolution image url
    for image in USGS_image_list:
        hemisphere_dict = {}

        # find link to large image
        href = image.find('a', class_='itemLink product-item')
        link = base_url + href['href']
        
        # Open the USGS site
        browser.visit(link)

        time.sleep(1)

        # Parse the html

        hemisphere_html_2 = browser.html
        hemisphere_soup_2 = bs(hemisphere_html_2, 'html.parser')

        # Find title
        img_title = hemisphere_soup_2.find('div', class_='content').find('h2', class_='title').text
        
        # Append to the hemisphere dictionary
        hemisphere_dict['title'] = img_title

        # find the image URL
        img_url = hemisphere_soup_2.find('div', class_='downloads').find('a')['href']
        
        # Append to the hemisphere dictionary
        hemisphere_dict['url_imgage'] = img_url

        # Append dictionary with hemisphere_image_urls list
    hemispheres_title_and_image.append(hemisphere_dict)

    return Mars_info_dict

