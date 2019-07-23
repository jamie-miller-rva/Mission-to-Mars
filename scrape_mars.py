# Dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd
import time

def init_browser():
    """ Sets a path to the browser (chrome) and identifies the location of the chromedriver"""

    executable_path = {'executable_path': 'chromedriver'} # chromedrive is in CWD
    return Browser('chrome', **executable_path, headless=False) # False to see the browser open

def scrape():
    """
    Scrape the following websites for Mars data
    Update the mongodb mission_to_mars db and mars_data collection
        with data collected (from scrape within the scrape_mars.py file)
        and store scraped in the Mars_info_dict (dictionary) 
        in the following order

            Mars_info_dict:

                # 1: ---------------------------------------------------
                Scrape NASA Mars News Site:  
                    Mars_info_dict["news_title"]
                    Mars_info_dict["news_paragraph"]
                
                # 2: ---------------------------------------------------
                Scrape Mars Weather twitter account:  
                    Mars Facts Web page in Mars_info_dict['mars_weather']
                
                # 3: --------------------------------------------------
                Scrape NASA Jet Propulsion Laboratory site: 
                    # (not used) Mars_info_dict['featured_image']
                    Mars_info_dict['featured_image_url']
                
                # 4: --------------------------------------------------
                Scrape USGS Astrogeology site:  
                    hemispheres_title_and_image = []
                
    """

    # Establish the Mars_info_dict (dictionary) to store scraped Mars information
    Mars_info_dict = {}

    #--------------------------------------------------------------
    # 1: Scrape the NASA Mars News Site
    #--------------------------------------------------------------
    # Use requests and Beautifulsoup  (bs) to scarpe NASA Mars News Site
    NASA_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    # Retrieve page with the requests module
    NASA_response = requests.get(NASA_url)

    # Create BeautifulSoup object; parse with 'lxml' parser (changed from html.parser)
    NASA_soup = bs(NASA_response.text, 'lxml') # use the 'lxml' parser

    # Get news title & paragraph description
    NASA_results = NASA_soup.find('div', class_='features')
    news_title = NASA_results.find('div', class_='content_title').text
    news_paragraph = NASA_results.find('div', class_='rollover_description').text

    # Add the title and description to the Mars_info_dict
    Mars_info_dict["news_title"] = news_title
    Mars_info_dict["news_paragraph"] = news_paragraph

    #--------------------------------------------------------------
    # 2: Scrape the Mars Weather twitter account
    #--------------------------------------------------------------
    mars_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    mars_twitter_response = requests.get(mars_twitter_url)    
    mars_twitter_soup = bs(mars_twitter_response.text, 'lxml')

    mars_twitter_result = mars_twitter_soup.find('div', class_='js-tweet-text-container')      
    mars_weather = mars_twitter_result.find('p', class_='js-tweet-text').text # Assign the scraped text to a variable 'mars_weather'
   
    # Store scraped data in dictionary
    Mars_info_dict['mars_weather'] = mars_weather

    #--------------------------------------------------------------
    # 3: Scrape the Mars Facts Web page
    #--------------------------------------------------------------

    # Mars Facts Table
    mars_facts_url = 'https://space-facts.com/mars/'
    mars_facts_table = pd.read_html(mars_facts_url)   
    Mars_Facts_df = mars_facts_table[1] # Create pandas DataFrame for second table containing just "Mars" Facts 
    
    # Cleanup the table
    Mars_Facts_df.columns = ["", "MARS PLANET PROFILE"]
    Mars_Facts_df.set_index("MARS PLANET PROFILE", inplace=True)       
 
    #Convert the data to a HTML table string.
    mars_facts = Mars_Facts_df.to_html()
    mars_facts.replace("\n","")    
    Mars_Facts_df.to_html('mars_facts.html')

    # Store html file in dictionary
    Mars_info_dict['mars_facts'] = mars_facts

    #--------------------------------------------------------------
    # 4: Scrape the NASA Jet Propulsion Laboratory site
    #--------------------------------------------------------------
    
    # Use splinter to navigate the JPL site and find the image url for the current 'featured_image' 
    # Call on chromedriver function to initalize browser for use with splinter
    browser = init_browser()

    # Open the JPL url using Chrome
    JPL_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(JPL_url) # opens up the JPL website

    JPL_html=browser.html # take out the information in html format
    JPL_soup = bs(JPL_html, 'lxml')

    # Get featured image
    featured_image = JPL_soup.find('div', class_='default floating_text_area ms-layer').find('footer')
    featured_image_url = 'https://www.jpl.nasa.gov'+ featured_image.find('a')['data-fancybox-href']

    # Add featured image url to dictionary
    # (not used) Mars_info_dict['featured_image'] = JPL_soup.find('div', class_='fancybox-inner fancybox-skin fancybox-dark-skin fancybox-dark-skin-open')
    Mars_info_dict['featured_image_url'] = featured_image_url

    #--------------------------------------------------------------
    # 5: Scrape the USGS Astrogeology site
    #--------------------------------------------------------------
    # Open the USGS url using Chrome
    USGS_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(USGS_url)

    # Retrieve the image string in html format for the full resolution hemisphere image, and the Hemisphere title containing the hemisphere name
    USGS_html = browser.html
    USGS_soup = bs(USGS_html, 'lxml')
    base_url ="https://astrogeology.usgs.gov" # need below

    USGS_image_list = USGS_soup.find_all('div', class_='item')

    # Create a list called hemisphere_title_and_image
    hemispheres_title_and_image = []    

    # Loop through each hemisphere and click on the link to find the large resolution image url
    for image in USGS_image_list:
        # Create a dictionary to store image titles and urls
        hemisphere_dict = {}

        # find link to large image
        href = image.find('a', class_='itemLink product-item')
        link = base_url + href['href']
        
        # Open the USGS site
        browser.visit(link)

        # Pause for 1 second
        time.sleep(1)

        # Parse the html
        hemisphere_html_2 = browser.html
        hemisphere_soup_2 = bs(hemisphere_html_2, 'lxml')

        # Find title
        img_title = hemisphere_soup_2.find('div', class_='content').find('h2', class_='title').text
        
        # Append to the hemisphere dictionary
        hemisphere_dict['title'] = img_title

        # find the image URL
        img_url = hemisphere_soup_2.find('div', class_='downloads').find('a')['href']
        
        # Append to the hemisphere dictionary
        hemisphere_dict['url_image'] = img_url
    
        # Append hemisphere_dict dictionary with hemispheres_title_and_image list
        hemispheres_title_and_image.append(hemisphere_dict)

    # Add hemispheres_title_and_image list to Mars_info_dict
    Mars_info_dict['hemispheres_title_and_image'] = hemispheres_title_and_image

    browser.quit()

    return Mars_info_dict # return scraped info in Mars_info_dict to the scraped app/function in app.py

