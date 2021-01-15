from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random
import csv




def find_link(tag_name):
    delay = 30
    try:
        element_present = EC.presence_of_element_located((By.XPATH, tag_name))
        WebDriverWait(driver, delay).until(element_present)
        driver.find_element_by_xpath(tag_name).click()
    except TimeoutException:
        print("Timed out waiting for page to load")



driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\Old Stuff\webscraping\chromedriver.exe')
driver.get('https://faces.fta.dot.gov/suite/')
driver.find_element_by_xpath('//*[@id="notification"]/div[2]/div/div/input').click()
elem = driver.find_element_by_name('un')
elem.send_keys('schumen@wsdot.wa.gov')
elem2 = driver.find_element_by_name('pw')
elem2.send_keys('Mroshhashanah4:1')
driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/div/div[2]/input').click()
find_link('//*[@id="sitesBody"]/div/div/div/div/div/div[4]/div/div[1]/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div[2]/div/div[2]/div/p')




