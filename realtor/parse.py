from datetime import datetime
from collections import namedtuple
import os
import pandas as pd
from bs4 import BeautifulSoup
import re

PropertyDetails = namedtuple('PropertyDetails', ['price', 'address', 'features', 'is_active', 'url'])

def parse_property_listing_info(div):
    price = None
    address = None
    url = None
    
  
    price_element = div.find('div', {'data-testid': 'card-price'})
    price = "No price available"
    if price_element:
        price = price_element.find('span').text.strip()

    
    address_element = div.find('div', {'data-testid': 'card-address-2'})
    address = "No address available"
    if address_element:
        address = address_element.text.strip()


    features = []
    ul_element = div.find('ul')
    if ul_element:
       
        li_elements = ul_element.find_all('li')
        for feature in li_elements:
            features.append(feature.text.strip())

    features_text = ', '.join(features) if features else 'No features available'


    status = 'No status available'
    status_element = div.find('div', {'data-testid': "card-description"})
    if status_element:
        status = status_element.find('div', 'message').text.strip()
    
    property_details = PropertyDetails(price, address, features_text, status, url)

    return property_details


def main():
    listings_dir = './listings'
    if not os.path.exists(listings_dir):
        print(f"Error: The directory '{listings_dir}' does not exist.")
        return

    realtor_files = os.listdir(listings_dir)
    if not realtor_files:
        print(f"No HTML files found in '{listings_dir}'.")
        return

    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory '{data_dir}' for output CSV files.")

    for html_file in realtor_files:
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

        property_div_elements = soup.find_all('div', id=re.compile('placeholder_property_*'))
        if not property_div_elements:
            print(f"No 'div' elements found in '{html_file}'.")
            continue

        property_listings = []
        
        for div_element in property_div_elements:
            property_info = parse_property_listing_info(div_element)
            property_listings.append(property_info)
        

 
        if property_listings:
            timestamp = datetime.now().strftime('%Y%m%d')
            df = pd.DataFrame(property_listings)

            output_file = os.path.join(data_dir, f'realtor_{timestamp}_{pageNum}.csv')
            try:
                df.to_csv(output_file, index=False)
                print(f"Saved data to '{output_file}'.")
            except Exception as e:
                print(f"Error saving CSV file '{output_file}': {e}")
        else:
            print(f"No property listings found in '{html_file}'.")
    
main()


