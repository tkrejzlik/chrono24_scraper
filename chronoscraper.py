from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class ChronoScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.watches = []

    def __get_links(self):
        self.__click_cookie_button()
        brand_list = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "brand-list")))
        html = brand_list.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        hrefs = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if 'index' not in href:
                continue
            hrefs.append(href)
        return hrefs

    def __click_cookie_button(self):
        self.driver.get("https://www.chrono24.com/search/browse.htm?char=A-Z")
        cookie_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-full-width.js-cookie-submit.wt-consent-layer-accept-all")))
        cookie_button.click()

    def get_watches(self):
        links = self.__get_links()
        base_url = 'https://www.chrono24.com'
        for link in links:
            self.__get_watches_from_site(base_url + link + "?pageSize=120")
            next_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'paging-next')))
            next_button.click()
            #   vyřešit tu pičovinu s kliknutím na next page a pak zavolat get_watches_from_site(selenium.current_url())

    def __get_watches_from_site(self, link):
        self.driver.get(link)
        watches_on_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "wt-watches")))
        html = watches_on_page.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        list_of_watches_per_site = soup.find_all("div", class_="p-x-2 p-x-sm-0")
        for watch in list_of_watches_per_site:
            soup = BeautifulSoup(str(watch), 'html.parser')
            data = soup.get_text()
            parsed_data = [line.strip() for line in data.split('\n') if line.strip()]
            self.watches.append(parsed_data)


chrono_scraper = ChronoScraper()
chrono_scraper.get_watches()
