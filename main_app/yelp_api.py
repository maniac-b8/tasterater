import requests
import os


API_KEY = os.getenv('YELP_API_KEY')
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'


def search_businesses(term=None, location=None, category=None):
    url = f"{API_HOST}{SEARCH_PATH}"
    headers = {
        'Authorization' : f"Bearer {API_KEY}"
    }
    params = {
        'limit': 10
    }
    if term:
        params['term'] = term
    if location:
        params['location'] = location
    if category:
        params['categories'] = category
    response = requests.get(url, headers=headers, params=params)
    return response.json()



def get_business_details(yelp_id):
    url = f"{API_HOST}{BUSINESS_PATH}{yelp_id}"
    headers = {
        'Authorization' : f"Bearer {API_KEY}"
    }       
    response = requests.get(url, headers=headers)
    return response.json() 