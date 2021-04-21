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

def find_tamp_text(tag_name):
    delay = 30
    try:
        element_present = EC.presence_of_element_located((By.LINK_TEXT, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        driver.find_element_by_link_text(tag_name).click()
        try:
            element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/button'))
            WebDriverWait(driver, delay).until(element_present)
            driver.find_element_by_xpath('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/button').click()
            try:
                element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[2]/div/div[2]/div[2]/div/p/a'))
                WebDriverWait(driver, delay).until(element_present)
                driver.find_element_by_xpath('//*[@id="related-action-body"]/div/main/div/div/div/div/div/div[2]/div/div[2]/div[2]/div/p/a').click()
            except TimeoutException:
                print("Timed out waiting for page to load")
        except TimeoutException:
            print("Timed out waiting for page to load")
    except TimeoutException:
        print("Timed out waiting for page to load")


df = pd.read_excel(r'C:\Users\SchumeN\Documents\NTD\a90list.xlsx')
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
    find_tamp_text('Transit Asset Management Performance Measure Targets (A-90)')
    driver.close()
