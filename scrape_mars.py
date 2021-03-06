from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
from time import sleep
import requests
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    m2m_data = {}

    # ## NASA Mars News
    # regular scrapping attempted, but html pulled is not the same as the one displayed
    # Use splinter to navigate the site and find the image url for the current Featured Mars Image and assign the url string to a variable
    browser = init_browser()

    # URL of page to be scraped
    mars_news_url = 'https://mars.nasa.gov/news/'

    # initialize
    nasa_mars_news = []

    browser.visit(mars_news_url)

    html = browser.html
    soup_result = BeautifulSoup(html, 'html.parser')

    # Retrieve the parent divs for all articles
    result = soup_result.find(class_='list_text')
    news_title = result.find(class_='content_title').text
    news_p = result.find(class_='article_teaser_body').text
    nmn = {
        "news_title":   news_title,
        "news_p": news_p,
    }
    nasa_mars_news.append(nmn)
    browser.quit()

    # ## JPL Mars Space Images - Featured Image

    # # Use splinter to navigate the site and find the image url for the current Featured Mars Image and assign the url string to a variable

    # first page
    # JPL Featured Space Image
    browser = init_browser()

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(url)

    browser.click_link_by_partial_text('FULL IMAGE')
    sleep(10)

    # second page
    browser.click_link_by_partial_text('more info')

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    image_urls = soup.find_all('div', class_='download_tiff')

    for image_url in image_urls:
        if "JPG" in image_url.text:
            featured_image_url = image_url.find('a')['href']
        else:
            continue

    featured_image_url =  'https:'+ featured_image_url

    # close browser
    browser.quit()

    # ## Mars Weather

    # URL of page to be scraped
    # Mars Weather twitter account
    mars_weather_twitter_url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response = requests.get(mars_weather_twitter_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')

    # Retrieve the parent divs for all articles
    results = soup.find_all(class_='js-tweet-text-container', limit=1)
    # print(results)
    # Loop through results
    for result in results:
        mars_weather = result.find(class_='TweetTextSize').text
        time_link = result.find(class_='twitter-timeline-link').text

    mars_weather = mars_weather.split(time_link)[0]

    ## Mars Facts

    # Mars Facts webpage
    mars_facts_url = 'http://space-facts.com/mars/'
    # Use Panda's `read_html` to parse the url

    tables = pd.read_html(mars_facts_url)[0]
    tables.columns = ['Description', 'Facts']
    mars_facts = []
    for r in tables.iterrows():
        mf = {
        "Description":  r[1]['Description'],
        "Facts": r[1]['Facts'],
        }
        mars_facts.append(mf)

    # Mars Hemispheres

    # USGS Astrogeology site
    astrogeology_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # initialize
    hemisphere_image_urls = []

    # Use splinter to navigate the site and find the image url for the current Featured Mars Image and assign the url string to a variable
    browser = init_browser()
    browser.visit(astrogeology_url)

    # Retrieve page with the requests module
    response = requests.get(astrogeology_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')

    # Retrieve the parent divs for all articles
    hemisphere_results = soup.find_all(class_='itemLink')
    # Loop through results
    for result in hemisphere_results:
        title = result.find(class_='description').text
        browser.click_link_by_partial_text(title)
        html = browser.html
        soup_result = BeautifulSoup(html, 'html.parser')
        image_urls = soup_result.find(class_='content').find(
            class_='block').find('dl').find('dd').find_next('dd')
        for image_url in image_urls:
            try:
                img_url = image_url['href']
                img_url_jpg = img_url +'/full.jpg'
                hiu = {
                    "title":   title,
                    "img_url": img_url_jpg,
                }
                hemisphere_image_urls.append(hiu)
            except:
                continue
    #   always go back to the initial url window
        browser.back()

    # close browser
    browser.quit()

    # Combined
    m2m_data["LatestMarsNews"] = nasa_mars_news
    m2m_data["FeaturedMarsImage"] = featured_image_url
    m2m_data["CurrentWeatheronMars"] = mars_weather
    m2m_data["MarsFacts"] = mars_facts
    m2m_data["MarsHemispheres"] = hemisphere_image_urls

    return m2m_data
