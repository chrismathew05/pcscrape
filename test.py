from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import os
import time
import json
import traceback
import logging
from tempfile import mkdtemp

# Log settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("output.log")
file_handler.setLevel(logging.INFO)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def wait_page_ready(
    driver: object, wait_interval: int = 1, max_wait: int = 120
) -> None:
    """Waits until web page on driver is fully loaded

    :param driver: selenium web driver
    :param wait_interval: wait time before page checks, defaults to 1
    :param max_wait: total amount of time to wait before failing, defaults to 120
    """

    wait = 0
    page_state = "Waiting..."
    while page_state != "complete" and wait < max_wait:
        page_state = driver.execute_script("return document.readyState;")
        time.sleep(wait_interval)
        wait += wait_interval


def init_driver() -> object:
    """Initializes selenium chromedriver for scraping

    :return: chrome webdriver to perform scraping
    """

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--log-level=OFF")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--enable-javascript")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
        service_log_path=os.devnull,
    )
    return driver


def main():
    """Starting point for script"""

    # obtain product codes from config file
    prods = []
    with open("config.json") as file:
        config_dict = json.load(file)
        prods = config_dict["_PRODUCT_CODES"]

    # scrape via selenium
    driver = init_driver()
    for prod in prods:
        url = f"https://www.mcmaster.com/{prod}/"
        driver.get(url)
        wait_page_ready(driver)

        labels = driver.find_elements(
            By.XPATH, "//*[contains(@class, 'attr-cell--table divider--spec-tbl')]"
        )
        vals = driver.find_elements(
            By.XPATH, "//*[contains(@class, 'divider--spec-tbl value-cell--table')]"
        )

        logger.info(f"\nPULLING INFO FOR: {prod} [{url}]")
        for idx, label in enumerate(labels):
            if label.text != "":
                logger.info(f"{label.text}: {vals[idx].text}")

    driver.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(traceback.format_exc())

    logger.info("Script complete.")
