from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
import requests
import time
import datetime
import os

URL = "https://www.icaionlineregistration.org/LaunchBatchDetail.aspx"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "-5100517651"


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)


def send_telegram(msg):
    log("Sending Telegram notification...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        log("Telegram message sent successfully.")
    except Exception as e:
        log(f"Telegram error: {e}")


def check_batch():

    log("Starting ICAI batch check...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    log("Launching Chromium in headless mode...")
    driver = Chrome(options=options)

    try:

        log("Opening ICAI batch page...")
        driver.get(URL)

        log("Selecting region: Southern")
        region = Select(driver.find_element(By.ID, "ddl_reg"))
        region.select_by_visible_text("Southern")

        time.sleep(1)

        log("Selecting POU: Chennai")
        pou = Select(driver.find_element(By.ID, "ddlPou"))
        pou.select_by_visible_text("MADURAI")

        time.sleep(1)

        log("Selecting course: AICITSS - Advanced Information Technology")
        course = Select(driver.find_element(By.ID, "ddl_course"))
        course.select_by_visible_text(
            "AICITSS - Advanced Information Technology"
        )

        time.sleep(1)

        log("Clicking 'Get List' button...")
        driver.find_element(By.ID, "btn_getlist").click()

        log("Waiting for results to load...")
        time.sleep(2)

        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
        
        seats_available = False
        log("Checking page content for batch availability...")
        
        for row in rows[1:]:  # skip header
            try:
                seats = row.find_element(By.XPATH, "./td[2]").text.strip()
                seats = int(seats.replace(",", ""))
                batch = row.find_element(By.XPATH, "./td[1]").text
            except:
                continue

            if seats > 0:
                seats_available = True
                break

        if seats_available:
           msg = f"🚨 ICAI AICITSS Batch OPENED for Chennai and seats available in {batch}!"
           print(f"🚨 BATCH OPEN WITH AVAILABLE SEATS in {batch}!")
           print(f"Batch: {batch} | Seats detected: {seats}")
           send_telegram(msg)
        elif len(rows) > 1:
           print("Batch exists but seats are FULL.")
        else:
           print("No batch available yet.")
    finally:
        log("Closing browser.")
        driver.quit()
        log("Check completed.\n")


if __name__ == "__main__":

    check_batch()
