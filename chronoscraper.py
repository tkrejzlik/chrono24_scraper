from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
driver.get("https://www.chrono24.com/search/browse.htm?char=A-Z")
cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.btn-full-width.js-cookie-submit.wt-consent-layer-accept-all")))
cookie_button.click()
page_source = driver.page_source


x=2
driver.quit()


