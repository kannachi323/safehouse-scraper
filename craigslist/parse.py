import requests
from bs4 import BeautifulSoup
import csv
import time
import pytz
from datetime import datetime

base_url = "https://sfbay.craigslist.org/search/scz/house-for-rent"

# get the soup object from a URL
def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

# extract listing URLs from one page
def get_listing_urls(soup):
    listing_urls = []
    for result in soup.find_all('li', class_='cl-static-search-result'):
        link = result.find('a')['href']
        listing_urls.append(link)
    return listing_urls

# extract details from a listing page
def get_listing_details(listing_url):
    soup = get_soup(listing_url)
    
    # try to get the details from the listing page
    try:
        street_address = soup.find('div', class_='mapaddress').text if soup.find('div', class_='mapaddress') else 'N/A'
        price = soup.find('span', class_='price').text if soup.find('span', class_='price') else 'N/A'
        housing = soup.find('span', class_='housing').text.strip() if soup.find('span', class_='housing') else 'N/A'
        
        # try to get the Google Maps URL from the href inside <a target="_blank"> within the mapbox
        map_link_tag = soup.find('a', target='_blank')
        map_link = map_link_tag['href'] if map_link_tag else 'N/A'
        
        return {
            'url': listing_url,
            'street_address': street_address,
            'price': price,
            'housing': housing,
            'map_address': map_link
        }
    except Exception as e:
        print(f"Error extracting data from {listing_url}: {e}")
        return {}


# get the next page URL
def get_next_page(soup):
    next_button = soup.find('a', class_='button next')
    return next_button['href'] if next_button else None

# main fucntion
def scrape_craigslist():
    page_url = base_url
    all_listings = []
    
    while page_url:
        print(f"Scraping page: {page_url}")
        soup = get_soup(page_url)
        
        # get listing urls from the current page
        listing_urls = get_listing_urls(soup)
        
        # extract details from each url
        for url in listing_urls:
            print(f"Scraping listing: {url}")
            details = get_listing_details(url)
            if details:
                all_listings.append(details)
        
        # get the next page url
        next_page = get_next_page(soup)
        if next_page:
            page_url = "https://sfbay.craigslist.org" + next_page
        else:
            page_url = None
        
        # hardcoded to try not get blacklisted
        time.sleep(2)
    
    return all_listings

# save to csv file
def save_to_csv(listings):
    # set to Pacific Time Zone (PDT) and get the time
    pacific = pytz.timezone('America/Los_Angeles')
    now_pdt = datetime.now(pacific)
    filename = f"data/{now_pdt.strftime('%Y-%m-%d %H-%M')}.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['url', 'street_address', 'price', 'housing', 'google_map_url'])
        writer.writeheader()
        for listing in listings:
            writer.writerow(listing)
    
    print(f"Data saved to {filename}")

# Run the scraper
listings = scrape_craigslist()
save_to_csv(listings)
