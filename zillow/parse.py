from datetime import datetime
from collections import namedtuple
import os
import pandas as pd
from bs4 import BeautifulSoup

PropertyDetails = namedtuple('PropertyDetails', ['price', 'address', 'features', 'is_active', 'url'])

def parse_property_listing_info(article):
    price = None
    address = None
    url = None
    
  
    price_element = article.find('span', {'data-test': 'property-card-price'})
    if price_element:
        price = price_element.text.replace('$', '').replace(',', '').strip()


    address_element = article.find('address', {'data-test': 'property-card-addr'})
    if address_element:
        address = address_element.text.strip()
 
        parent_element = address_element.parent
        if parent_element and parent_element.has_attr('href'):
            url = parent_element['href']


    price = price if price else 'No price available'
    address = address if address else 'No address available'
    url = url if url else 'No URL available'

    features = []


    ul_element = article.find('ul')
    if ul_element:
       
        li_elements = ul_element.find_all('li')
        if li_elements:
            
            features = [feature.text.strip() for feature in li_elements]


    features_text = ', '.join(features) if features else 'No features available'


    status = 'No status available'
    if ul_element:
        parent_element = ul_element.parent
        if parent_element:
            text = parent_element.get_text(strip=True)
            if '-' in text:
                status = text.split('-')[-1].strip()

    
    property_details = PropertyDetails(price, address, features_text, status, url)

    return property_details


def main():
    listings_dir = './listings'
    if not os.path.exists(listings_dir):
        print(f"Error: The directory '{listings_dir}' does not exist.")
        return

    zillow_files = os.listdir(listings_dir)
    if not zillow_files:
        print(f"No HTML files found in '{listings_dir}'.")
        return

    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory '{data_dir}' for output CSV files.")

    for html_file in zillow_files:
      
        if not html_file.lower().endswith('.html'):
            print(f"Skipping non-HTML file: {html_file}")
            continue

        pageNum = os.path.splitext(html_file)[0].split('_')[1]
        print(f"Processing file: {html_file}")

        file_path = os.path.join(listings_dir, html_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        except Exception as e:
            print(f"Error reading '{html_file}': {e}")
            continue

        property_article_elements = soup.find_all('article')
        if not property_article_elements:
            print(f"No 'article' elements found in '{html_file}'.")
            continue

        property_listings = []

        for article_element in property_article_elements:
            property_info = parse_property_listing_info(article_element)
            property_listings.append(property_info)

        if property_listings:
            timestamp = datetime.now().strftime('%Y%m%d')
            df = pd.DataFrame(property_listings)

            output_file = os.path.join(data_dir, f'zillow_{timestamp}_{pageNum}.csv')
            try:
                df.to_csv(output_file, index=False)
                print(f"Saved data to '{output_file}'.")
            except Exception as e:
                print(f"Error saving CSV file '{output_file}': {e}")
        else:
            print(f"No property listings found in '{html_file}'.")

main()


