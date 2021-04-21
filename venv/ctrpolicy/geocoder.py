
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyCFZtdkwSnbz8nLm3QwSOtwET0hkVA4lKM')

geocode_result = gmaps.geocode('416 Sid Snyder Ave SW 98501 WA')

print(geocode_result)