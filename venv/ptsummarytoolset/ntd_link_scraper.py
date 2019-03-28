from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import bs4
import time
import random
import csv

def find_link(tag_name):
    delay = 60
    try:
        element_present = EC.presence_of_element_located((By.XPATH, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        driver.find_element_by_xpath(tag_name).click()
    except TimeoutException:
        print("Timed out waiting for page to load")

def to_csv(res, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        try:
            writer.writerows([res])
        except:
            pass

driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')
driver.get('https://faces.fta.dot.gov/suite/')
driver.find_element_by_xpath('//*[@id="notification"]/div[2]/div/div/input').click()
elem = driver.find_element_by_name('un')
elem.send_keys('schumen@wsdot.wa.gov')
elem2 = driver.find_element_by_name('pw')
elem2.send_keys(',yB>LjuE$3@v')
driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/div/div[2]/input').click()
find_link('/html/body/div[7]/div[1]/div/div[1]/a[3]')
find_link('/html/body/div[7]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[2]/div/div[2]/div[2]/div/div[2]/div/div/div[3]/div/div[1]/a')
delay = 60

try:
    element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div[7]/div[2]/div/div[2]/div/div[2]/div[2]/div/tempo-record-list/div/main/div/div/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/p/a'))
    WebDriverWait(driver, delay).until(element_present)
except TimeoutException:
    print("Timed out waiting for page to load")

inner_html = driver.page_source
links = []
agency_name = []
soup = bs4.BeautifulSoup(inner_html)
for link in soup.find_all('a', href = True):
    links.append(link['href'])
for link in soup.find_all('strong'):
    agency_name.append(link.text)

res = links+agency_name
to_csv(res, r'C:\Users\SchumeN\Documents\NTD\ntdlinks.csv')