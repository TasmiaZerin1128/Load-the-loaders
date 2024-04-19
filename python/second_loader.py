import requests
import os
from modules.utils import auth_token_generator, curve_file_generator

def fetch_data(auth_token: str):
    
    data_url = "https://api.terna.it/transparency/v1.0/getrenewablegeneration?dateFrom=2/2/2021&dateTo=15/2/2021&type=Hydro&type=Wind"
    headers = {
        "Authorization": "Bearer " + auth_token,
        "Accept": "Application/Json"
    }

    response = requests.get(data_url, headers=headers)
    data = response.json()
    print(data['renewableGeneration'])
    return data

def save_data(data_list: dict):
    generator = curve_file_generator.CurveGenerator(data_list)
    generator.createCSV('terna_renewable_report')

def get_results() -> None:
    url = "https://api.terna.it/transparency/oauth/accessToken"
    auth_token = auth_token_generator.AuthToken(url).create_terna_request()
    result = fetch_data(auth_token)
    print(auth_token)
    save_data(result)


get_results()