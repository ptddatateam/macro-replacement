from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import random
import csv


driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')

def scrape():
    time.sleep(random.uniform(0, 3))
    links = driver.find_elements_by_tag_name('a')
    linklist = []
    for i in links:
        try:
            linklist.append(i.get_attribute('href'))
        except:
            continue
    links = [j for j in linklist if 'Overview' in j]
    links = list(set(links))
    to_csv(links, r'C:\Users\SchumeN\Documents\CTR\webscraping\links.csv')

def to_csv(res, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        try:
            writer.writerows([res])
        except:
            pass

'''while True:
    try:
        scrape()
        attribute = driver.find_element_by_xpath('//*[@id="FooterPageNav"]/div/ul/li[7]/a')
        newlink = attribute.get_attribute('href')
        driver.get(newlink)
    except:
        break'''


df = pd.read_csv(r'C:\Users\SchumeN\Documents\CTR\webscraping\links.csv')
for i in df.links[4479:]:
    resultlist = []
    time.sleep(random.uniform(0, 3))
    driver.get(i)
    #size = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[3]/span')
    #size = size.text
    #hq = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[2]/span')
    #hq = hq.text
    companyname = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/header/h2')
    companyname = companyname.text
    companyname = companyname.replace(' Overview', '')
    try:
        website = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[1]/span/a')
        website = website.get_attribute('href')
    except:
        website = 'Unknown'
    try:
        industry = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[6]/span')
        industry = industry.text
    except:
        industry = 'Unknown'
    try:
        type = driver.find_element_by_xpath('//*[@id="EmpBasicInfo"]/div[1]/div/div[5]/span')
        type = type.text
    except:
        type = 'Unkown'
    resultlist.append(type)
    resultlist.append(industry)
    resultlist.append(companyname)
    resultlist.append(website)
    to_csv(resultlist, r'C:\Users\SchumeN\Documents\CTR\webscraping\seattleindustryandtypecompanies.csv')




