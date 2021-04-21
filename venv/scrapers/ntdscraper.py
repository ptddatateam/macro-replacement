from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
import pandas as pd
import time
import random
import csv



def find_ntd_page(driver):
    count = 1
    full_links = []
    driver.get('https://www.transit.dot.gov/ntd/ntd-data')
    while count < 46:
        link_list = []
        links = driver.find_elements_by_tag_name('tr')
        for i in links:
            link = driver.find_elements_by_tag_name('a')
            for i in link:
                try:
                    result = i.get_attribute('href')
                    try:
                        link_list.append(result)
                    except TypeError:
                        continue
                except StaleElementReferenceException:
                    continue
                except NoSuchElementException:
                    break
        full_links += link_list
        count += 1
        elem = driver.find_element_by_class_name('pager-next')
        elem.click()
    return full_links

def to_csv(res, path):
    newpath = path + '\links.csv'
    with open(newpath, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        try:
            writer.writerows([res])
        except:
            pass


def main(path):
    driver = webdriver.Chrome(r'C:\Users\SchumeN\Documents\webscraping\chromedriver.exe')
    full_links = find_ntd_page(driver)
    to_csv(full_links, path)
if __name__ == "__main__":
    main(r'C:\Users\SchumeN\Documents\databaseproject\ntddata')
