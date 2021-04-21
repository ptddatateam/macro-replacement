import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
import csv
from yelpapi import YelpAPI
from googleplaces import GooglePlaces, types, lang
import requests
import re
import xml.etree.ElementTree as ET



yelp_api = YelpAPI('cbtMcir_cmrSfmai5VVrM3k65byUAzjzgHHUyjlIpEnvIGSp9q6-z6Y7Z5AXrksEsU5GnZFzNh80MMoqvUPBHTatFYAH3JLEzeIOTyOnnFxNBY5MrVBDXxOGD_UeW3Yx')

df = pd.read_excel(r'C:\Users\SchumeN\Documents\CTR\webscraping\Seattleresults\secondtierconfidence.xlsx')

def to_csv(res, path):
    with open(path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter = ',')
        try:
            writer.writerows([res])
        except:
            pass
 # yelp address finder
''' for i in df.name:
    i = i.replace(' ', '-')

    try:
        response = yelp_api.business_query('{}-Seattle'.format(i))
        to_csv([i, response['name'], response['location']['display_address']], path')
    except yelp_api.YelpAPIError as e:
        continue
        
'''

def find_business(name, apikey):
    req = 'http://api2.yp.com/listings/v1/search?searchloc=Seattle+wa&term={}&format=json&key={}&sort=name'.format(name, apikey)
    response = requests.get(req)
    response = response.json()
    try:
        if response['searchResult']['metaProperties']['listingCount'] == 0:
            return False
        else:
            responsesearch = response['searchResult']['searchListings']['searchListing']
            for i in responsesearch:
                if i['city'] == 'Seattle':
                    to_csv([i['businessName'], i['street'], i['city'], i['zip'], i['phone']],
                           'C:\\Users\\SchumeN\\Documents\\CTR\\webscraping\\Seattleresults\\yellowpagesaddresses.csv')
    except KeyError:
        return False


apikey = '24jxp36353'
for i in df.name:
    response = find_business(i, apikey)
    if response == False:
        continue