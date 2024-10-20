import time
import sys
from playwright.sync_api import sync_playwright

def download_realtor_page(page, zip_code, pageNum):
    if pageNum == '1':
        page_ext = ''
    else:
        page_ext = 'pg' + pageNum


    url = f"https://realtor.com/apartments/{zip_code}/{page_ext}"
    
    for _ in range(3):
        print("trying again")
        response = page.goto(url, wait_until='domcontentloaded')
        
        if response.status == 404:
            print(f"Page not found for {url}")
            return False
        
        time.sleep(2)

        if not page.title().startswith(f"Apartments for Rent in {zip_code}"):
            print(f"Incorrect page title for {url}. Retrying...")
            page.close()
            time.sleep(5)
            page = page.browser.new_page(java_script_enabled=True)
            continue

        target_element = page.locator('.PropertiesList_propertiesContainer__Vox4I.PropertiesList_listViewGrid__bttyS')
        if not target_element:
            print("Couldn't find the properties container.")
            continue
        
        try:
            for _ in range(12):
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(2)
        except Exception as e:
            print(f"Scrolling failed: {e}")
            return False
        
        try:
            with open(f'./listings/realtor_{pageNum}.html', 'w', encoding='utf-8') as f:
                f.write(target_element.inner_html())
            print(f"Successfully saved realtor_{pageNum}.html")
            return True
        except Exception as e:
            print(f"Failed to save file realtor_{pageNum}.html: {e}")
            return False

    return False
playwright = sync_playwright().start()

browser = playwright.chromium.launch(
    headless=False,
    args=["--disable-blink-features-AutomationControlled"]
)

if len(sys.argv) < 2:
    raise Exception("Must provide page number")

pageNum = sys.argv[1]


page = browser.new_page(java_script_enabled=True)
if not download_realtor_page(page, "95060", pageNum):
    raise Exception('Page not found')