from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

import re
import unicodedata

def clean_description(text):
    # Normalize unicode to remove accents/symbols
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

    # Replace any kind of newline variations with '\n'
    text = re.sub(r'\r\n|\r|\n', '\n', text)

    # Remove any character not in the whitelist
    allowed_chars = re.compile(r"[^A-Za-z0-9\s\n\.\,\:\;\!\?\-\_\=\'\"\(\)\[\]\/\@\#\$\%\&\*\+\=]")
    text = allowed_chars.sub('', text)

    # Replace multiple spaces or tabs with a single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Clean up leading/trailing spaces on each line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


# Setup the WebDriver
driver = webdriver.Chrome()

seen_category_links = set()
base_url = "https://www.g2g.com/trending/software?page={}"

# Collect data
data = []

for page in range(5, 10):  # 1 to 11
    driver.get(base_url.format(page))
    time.sleep(5)

    # Find all product cards
    cards = driver.find_elements(By.CSS_SELECTOR, "a.cursor-pointer.g-card-no-deco.swiper-no-swiping")

    for card in cards:
        try:
            link = card.get_attribute("href")
            # Skip if already processed
            if link in seen_category_links:
                continue

            seen_category_links.add(link)

            category_elem = card.find_elements(By.CSS_SELECTOR, "div.ellipsis-2-lines")
            category = category_elem[0].text.strip() if len(category_elem) > 0 else ""

            # Extract background image URL
            background_image_elem = card.find_element(By.CSS_SELECTOR, "div[style*='background-image']")
            style_attribute = background_image_elem.get_attribute("style")
            
            # Extract the URL from the style attribute (it should be inside the url("..."))
            start = style_attribute.find("url(") + 4
            end = style_attribute.find(")", start)
            image_url = style_attribute[start:end].strip(' "')

            # Visit the category link to extract sub-categories
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            time.sleep(5)

            # Find sub-category blocks
            sub_cards = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-12.col-sm-6.col-md-3")

            for sub in sub_cards:
                try:
                    sub_name_elem = sub.find_element(By.CSS_SELECTOR, "div.text-body1.ellipsis-2-lines span")
                    sub_name = sub_name_elem.text.strip()

                    sub_price_elem = sub.find_element(By.CSS_SELECTOR, "div.row.items-baseline span:nth-of-type(2)")
                    price = sub_price_elem.text.strip()

                    sub_link_elem = sub.find_element(By.CSS_SELECTOR, "a")
                    sub_link = sub_link_elem.get_attribute("href")

                    # Open sub-category in another new tab to get the detail
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[2])
                    driver.get(sub_link)
                    time.sleep(5)

                    try:
                        detail_elem = driver.find_element(By.CSS_SELECTOR, "p.q-mb-none")
                        detail_text_raw = detail_elem.text.strip()
                        detail_text = clean_description(detail_text_raw)
                    except:
                        detail_text = "No description."

                    # Append all data
                    sr_no = len(data) + 1
                    data.append([sr_no, category, link, image_url, sub_name, price, sub_link, detail_text])

                    driver.close()
                    driver.switch_to.window(driver.window_handles[1])

                except Exception as sub_e:
                    print("Error parsing sub-category:", sub_e)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print("Error while scraping a category card:", e)
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

# Save to CSV
csv_filename = "g2g_softwares1.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Sr No", "Category", "Category Link", "Background Image", "Sub-category", "Price (USD)", "Sub-category Link", "Description"])
    writer.writerows(data)

print("Data has been successfully saved to 'g2g_softwares1.csv'")
