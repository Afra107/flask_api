import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

driver = webdriver.Chrome()

# Open the URL
url = "https://www.g2g.com/categories/wow-classic-boosting-service?sort=recommended_v2"
driver.get(url)

# Wait for page to load
time.sleep(5)

# Find all product cards
cards = driver.find_elements(By.CSS_SELECTOR, "a.full-height.column.g-card-no-deco")

# Collect data
data = []

for card in cards:
    try:
        title = card.text.split("\n")[0]
        link = card.get_attribute("href")

        # Min Purchase & Stock
        chip_counters = card.find_elements(By.CSS_SELECTOR, "div.g-chip-counter")
        min_purchase = chip_counters[0].text.strip() if len(chip_counters) > 0 else ""
        stock = chip_counters[1].text.strip() if len(chip_counters) > 1 else ""

        # Navigate to parent card to access price, currency, seller
        parent = card.find_element(By.XPATH, "./ancestor::div[contains(@class, 'col-xs-12')]")

        price_elem = parent.find_elements(By.CSS_SELECTOR, "span.text-body1.text-weight-medium")
        price = price_elem[0].text.strip() if price_elem else ""

        currency_elem = parent.find_elements(By.CSS_SELECTOR, "span.text-caption.q-ml-xs")
        currency = currency_elem[0].text.strip() if currency_elem else ""

        seller_elem = parent.find_elements(By.CSS_SELECTOR, "div.text-body2.ellipsis")
        seller = seller_elem[0].text.strip() if seller_elem else ""

        # Step 2: Visit product detail page
        driver.execute_script("window.open('');")  # Open new tab
        driver.switch_to.window(driver.window_handles[1])  # Switch to new tab
        driver.get(link)
        time.sleep(3)

        # Try to extract service details
        try:
            desc_elem = driver.find_element(By.ID, "profile-description")
            description = desc_elem.text.strip().replace("\n", " | ")
        except NoSuchElementException:
            description = "No details found"

        driver.close()  # Close the product tab
        driver.switch_to.window(driver.window_handles[0])  # Back to main tab

        # Save all info
        data.append([title, link, min_purchase, stock, price, currency, seller, description])

    except Exception as e:
        print("Error while scraping a card:", e)
        # In case detail tab fails to load, make sure we return
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

# Save to CSV
csv_filename = "g2g_boosting_data_with_details.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Link", "Min Purchase", "Available Stock", "Price", "Currency", "Seller", "Description"])
    writer.writerows(data)

print(f"Data saved to {csv_filename}")
driver.quit()
