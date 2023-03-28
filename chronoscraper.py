from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import sqlite3


class ChronoScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.conn = sqlite3.connect('chrono24.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS watches
                          (id INTEGER PRIMARY KEY,
                           brand TEXT,
                           name TEXT,
                           ext_name TEXT,
                           price TEXT,
                           ship TEXT,
                           location TEXT)
                           ''')

    def __save_and_close_database(self):
        self.conn.commit()
        self.conn.close()

    def __get_links(self):
        self.__click_cookie_button()
        brand_list = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "brand-list")))
        html = brand_list.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        hrefs = {}
        for link in soup.find_all('a'):
            href = link.get('href')
            if 'index' not in href:
                continue
            brand_name = link.get_text()
            hrefs.update({brand_name: href})
        return hrefs

    def __click_cookie_button(self):
        self.driver.get("https://www.chrono24.com/search/browse.htm?char=A-Z")
        cookie_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-full-width.js-cookie-submit.wt-consent-layer-accept-all")))
        cookie_button.click()
        time.sleep(3)
        ad_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'sticky-close')))
        ad_button.click()

    def get_watches(self):
        links = self.__get_links()
        base_url = 'https://www.chrono24.com'
        for brand, link in links.items():
            self.__get_watches_from_site(base_url + link + "?pageSize=120", brand)
            while True:
                try:
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'paging-next')))
                    next_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, 'paging-next')))
                    next_button.click()
                    time.sleep(0.5)
                    self.__get_watches_from_site(self.driver.current_url, brand)
                except TimeoutException:
                    break
        self.__save_and_close_database()

    def __get_watches_from_site(self, link, brand_name):
        self.driver.get(link)
        try:
            watches_on_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "wt-watches")))
        except (TimeoutException, NoSuchElementException):
            return
        html = watches_on_page.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        list_of_watches_per_site = soup.find_all("div", class_="p-x-2 p-x-sm-0")
        for watch in list_of_watches_per_site:
            soup = BeautifulSoup(str(watch), 'html.parser')
            data = soup.get_text()
            parsed_data = [line.strip() for line in data.split('\n') if line.strip()]
            try:
                self.c.execute("INSERT INTO watches (brand, name, ext_name, price, ship, location) VALUES (?, ?, ?, ?, ?, ?)",
                               (brand_name, parsed_data[0], parsed_data[1], parsed_data[2], parsed_data[3], parsed_data[4]))
            except IndexError:
                self.c.execute(
                    "INSERT INTO watches (id, brand, name, ext_name, price, ship, location) VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                    (brand_name, parsed_data[0] if len(parsed_data) > 0 else None,
                     parsed_data[1] if len(parsed_data) > 1 else None, parsed_data[2] if len(parsed_data) > 2 else None,
                     parsed_data[3] if len(parsed_data) > 3 else None,
                     parsed_data[4] if len(parsed_data) > 4 else None))


chrono_scraper = ChronoScraper()
chrono_scraper.get_watches()
