from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import random


driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')
driver.get('https://www.seattlechamber.com/home/resources/membership-directory')
basedf = pd.DataFrame(columns = ['name', 'address', 'city', 'url'])

def set_size(size):
    select = driver.find_element_by_id('HomepageContent_C025_dNumEmp')
    for option in select.find_elements_by_tag_name('option'):
        if option.text == size:
            option.click()
    submit = driver.find_element_by_xpath('//*[@id="HomepageContent_C025_btnGo"]')
    submit.click()
def get_next(index):
    print(index)
    xpath = '//*[@id="HomepageContent_C025_dirResultPager"]/a[{}]'.format(index)
    results = driver.find_element_by_xpath(xpath)
    results.click()
def find_info():
    namelist = []
    names = driver.find_elements_by_class_name('business_name')
    for name in names:
        namelist.append(name.text)
    addresslist = []
    address = driver.find_elements_by_class_name('address')
    for ad in address:
        addresslist.append(ad.text)
    citylist = []
    city = driver.find_elements_by_class_name('city_state')
    for civis in city:
        citylist.append(civis.text)
    urllist = []
    url = driver.find_elements_by_class_name('web_url')
    for urls in url:
        urllist.append(urls.text)
    df = pd.DataFrame()
    df['name'] = namelist
    df['address'] = addresslist
    df['city'] = citylist
    df['url'] = urllist
    df['category'] = '100-500'
    return df

set_size('100-500')
index = 1
while True:
    try:
        time.sleep(random.randint(0,5))
        get_next(index)
        newdf = find_info()
        basedf = pd.concat([basedf, newdf], axis = 0)
        print(len(basedf))
        index += 1
        if index == 7:
            index = 2
    except:
        break
basedf.to_csv(r'C:\Users\SchumeN\Documents\CTR\webscraping\scrape.csv')