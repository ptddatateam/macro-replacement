from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
import pandas as pd
import time
import random
import csv

driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')
df = pd.read_csv(r'C:\Users\SchumeN\Documents\databaseproject\ntddata\links.csv')
for i in df.links.tolist():
    driver.get(i)
    file = driver.find_element_by_xpath('//*[@id="content-article"]/div[1]/div/div/span/a')
    file.click()
