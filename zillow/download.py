import time
import sys
from playwright.sync_api import sync_playwright

def download_zillow_page(page, url, pageNum):
    for _ in range(3):
        response = page.goto(url, wait_until='domcontentloaded')
        if response.status == 404:
            return False

        time.sleep(2)

        if not page.title().startswith('Rental Listings'):
            page.close()
            time.sleep(5)
            page.browser.new_page(java_script_enabled=True)
            continue
  
        target_element = page.locator("#search-page-list-container")
        
        for _ in range(12):
            target_element.evaluate("element => element.scrollBy(0, 800)")
            time.sleep(1)
        
        with open(f'./listings/zillow_{pageNum}.html', 'w', encoding='utf-8') as f:
            f.write(target_element.inner_html())
        return True

playwright = sync_playwright().start()

browser = playwright.chromium.launch(
    headless=False,
    args=["--disable-blink-features-AutomationControlled"]
)

if len(sys.argv) < 2:
    raise Exception("Must provide page number")

pageNum = sys.argv[1]
if pageNum == '1':
    pageNum = '' 
else:
    pageNum = pageNum + '_p'


page = browser.new_page(java_script_enabled=True)
url = f"https://www.zillow.com/santa-cruz-ca-95060/rentals/{pageNum}"
if not download_zillow_page(page, url, pageNum):
    raise Exception('Page not found')