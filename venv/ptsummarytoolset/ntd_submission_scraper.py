from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import bs4
import time
import random
import csv
import os



def find_elem(tag_name):
    delay = 30
    try:
        element_present = EC.presence_of_element_located((By.XPATH, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        try:
            driver.find_element_by_xpath(tag_name).click()
        except WebDriverException:
            elem = driver.find_element_by_xpath(tag_name)
            link = elem.get_attribute('href')
            driver.get(link)
    except TimeoutException:
        print("Timed out waiting for page to load")

def find_link(tag_name):
    delay = 30
    try:
        element_present = EC.presence_of_element_located((By.XPATH, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        driver.find_element_by_xpath(tag_name).click()
    except TimeoutException:
        print("Timed out waiting for page to load")
def find_text(tag_name):
    delay = 120
    try:
        element_present = EC.presence_of_element_located((By.XPATH, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        elem = driver.find_element_by_xpath(tag_name)
        return elem.text
    except TimeoutException:
        print("Timed out waiting for page to load")


df = pd.read_csv(r'C:\Users\SchumeN\Documents\NTD\ntdlinks.csv')
zelda = df.links.tolist()
agencies = df.agency.tolist()
zipped = zip(zelda, agencies)
for website, agency in zipped:
    if os.path.exists(r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files\{}'.format(agency)) == False:
        os.makedirs(r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files\{}'.format(agency))
    download_dir = r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files\{}'.format(agency)
    chrome_options = webdriver.ChromeOptions()
    preferences = {"download.default_directory": download_dir,
                   "directory_upgrade": True,
                   "safebrowsing.enabled": True}
    chrome_options.add_experimental_option("prefs", preferences)
    driver = webdriver.Chrome(chrome_options= chrome_options, executable_path=r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')
    driver.get('https://faces.fta.dot.gov/suite/')
    driver.find_element_by_xpath('//*[@id="notification"]/div[2]/div/div/input').click()
    elem = driver.find_element_by_name('un')
    elem.send_keys('schumen@wsdot.wa.gov')
    elem2 = driver.find_element_by_name('pw')
    elem2.send_keys(',yB>LjuE$3@v')
    driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/div/div[2]/input').click()
#driver.get('https://faces.fta.dot.gov/suite/tempo/records/type/CfabgQ/view/all')

    driver.get('{}'.format(website))
    delay = 60

    try:
        element_present = EC.presence_of_element_located((By.TAG_NAME, 'button'))
        WebDriverWait(driver, delay).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

    driver.find_element_by_xpath('//*[@id="record-header"]/div/main/div/div/div/div[1]/div/div/div/div/div[2]/div/div[2]/button').click()
    row_count = len(driver.find_elements_by_tag_name('tr'))
    print(row_count)
    if row_count == 3:
        row_count = row_count -1
    else:
        row_count = row_count -3
    count = 1
    while count <= row_count:
        find_link('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div/div/div/div[2]/div/div[1]/table/tbody/tr[{}]/td[1]/div/p/a'.format(count))
        time.sleep(15)
        text = find_text('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[1]/div/div/div/h1')
        text = text.replace(' - DR DO', '')
        text = text.replace(' - VP DO', '')
        text = text.replace(' - CB DO', '')
        text = text.replace(' - MB DO', '')
        if 'Revenue Vehicle Inventory (A-30)' == text:
            find_link('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/button')
        elif 'Transit Asset Management Performance Measure' in text:
            find_link('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/button')
        elif 'Service Vehicle' in text:
            find_link('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/button')
        else:
            find_link('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[4]/button')
        find_link('/html/body/div[9]/div/div/div[2]/div[2]/div/div/button')
        try:
            find_elem('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[2]/div/div[2]/div[2]/div/p/a')
        except WebDriverException:
            pass
        driver.back()
        find_link('//*[@id="record-header"]/div/main/div/div/div/div[1]/div/div/div/div/div[2]/div/div[2]/button')
        count+=1
    driver.close()
#html = driver.page_source
#print(html)
#elem = driver.find_element_by_id('record-header')
#all_children_by_xpath = elem.find_elements_by_xpath(".//*")


