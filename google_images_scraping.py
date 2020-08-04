import base64
import os
import requests
import time
import argparse

from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# Configuration
download_path = "dataset"
chrome_driver_location = 'chromedriver.exe'

def check_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False

def save_images(thumbnail_src, target_save_location, i):
    is_b64 = check_b64(thumbnail_src)
    # Base64
    if is_b64:
        image_format = is_b64
        content = base64.b64decode(thumbnail_src.split(';base64')[1])
    # URL
    else:
        try:
            resp = requests.get(thumbnail_src, stream=True)
            temp_for_image_extension = BytesIO(resp.content)
            image = Image.open(temp_for_image_extension)
            image_format = image.format
            content = resp.content
        except:
            print('[INFO] Connection aborted!')
            return False

    with open(target_save_location+str(i)+'.'+str(image_format), 'wb') as f:
        f.write(content)


def launch_driver(search):

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    options = Options()
    #options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-cross-origin-auth-prompt")

    driver = webdriver.Chrome(executable_path=chrome_driver_location, options=options)
    driver.get(f"https://www.google.com/search?q=" + search + "&source=lnms&tbm=isch&sa=X")

    return driver

def launch_scraping(search_terms, nb_images, first_image, thb):
    # Create directories to save images
    os.makedirs(download_path, exist_ok=True)

    for search in search_terms:
        target_save_location = os.path.join(download_path, search.replace(" ", "_"), '')
        os.makedirs(target_save_location, exist_ok=True)

        # Launch driver
        driver = launch_driver(search)
        more_results_btn = False

        for i in range(nb_images):

            if i < first_image: continue

            print(i)

            # Load more images
            if i%50==0 and i!=0:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Get image
            try:
                image = driver.find_elements_by_xpath('//a/div/img')[i]
            except IndexError:
                if more_results_btn == False:
                    # Click on "Show more results" button
                    driver.find_elements_by_xpath('//input')[-1].click()
                    more_results_btn = True
                    time.sleep(2)

                    image = driver.find_elements_by_xpath('//a/div/img')[i]
                else:
                    print('[INFO] NO MORE IMAGES !')
                    break

            # Get thumbnail
            if thb==True:
                thumbnail_src = image.get_attribute("src")
                if thumbnail_src is None:
                    thumbnail_src = image.get_attribute("data-src")
                if thumbnail_src is None:
                    continue

                save_images(thumbnail_src, target_save_location, i)

            # Get large images
            else:
                image.click()
                right_panel = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'''//*[@data-query="{search}"]''')))
                # Wait for the first image to be loaded
                time.sleep(1)
                try:
                    panel_image = right_panel.find_elements_by_xpath('//*[@data-noaft="1"]')[0]
                except IndexError:
                    print('[INFO] IndexError: list index out of range')
                    continue

                magic_class = panel_image.get_attribute('class')
                image_finder_xp = f'//*[@class="{magic_class}"]'

                # [-2] element is the element currently displayed
                target = driver.find_elements_by_xpath(image_finder_xp)[-2]

                src = target.get_attribute("src")
                if src is None:
                    src = image.get_attribute("data-src")
                if src is None:
                    continue

                save_images(src, target_save_location, i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Google Images Scraper')
    parser.add_argument('--search', type=str, required=True, help='Search terms (list)', nargs='+')
    parser.add_argument('--images', type=int, required=False, default=600, help='Number of images to download (int)')
    parser.add_argument('--first', type=int, required=False, default=0, help='Position of the first images to download (int)')
    parser.add_argument('--thb', required=False, default=False, help='Download thumbnail (True) or large images (False)')
    args = parser.parse_args()

    launch_scraping(args.search, args.images, args.first, args.thb)
