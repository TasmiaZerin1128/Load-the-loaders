import requests
import os
import datetime
import sys
from modules.utils import auth_token_generator, curve_file_generator


def check_if_data_available_for(start_date: datetime.date):
    if start_date < datetime.date(year=2019, month=1, day=1):
        raise ValueError(f"{start_date} is prior to the data publish start date of January 1st, 2019.")
    if start_date > datetime.datetime.now().date() + datetime.timedelta(days=1):
        raise ValueError(f"{start_date} is in the future. Query date is supported till today's date.")

def fetch_data(auth_token: str, start_date: datetime.date, end_date: datetime.date):
    start_date = start_date.strftime('%-d/%-m/%Y')
    end_date = end_date.strftime('%-d/%-m/%Y')
    print(start_date)

    data_url = f"https://api.terna.it/transparency/v1.0/getrenewablegeneration?dateFrom={start_date}&dateTo={end_date}&type=Hydro&type=Wind&type=Photovoltaic"
    headers = {
        "Authorization": "Bearer " + auth_token,
        "Accept": "Application/Json"
    }

    response = requests.get(data_url, headers=headers)

    if 'Developer Inactive' in response.text: return None

    data = response.json()

    
    return data['renewableGeneration']


def save_data(data_list: dict):
    for data in data_list:
        data['date'] = data.pop('Date')
        data['value'] = data.pop('Renewable_Generation_GWh')
        data['keys'] = data.pop('Energy_Source')
        data['name'] = 'terna_renewable_report'

    generator = curve_file_generator.CurveGenerator(data_list)
    generator.createCSV('terna_renewable_report')

def get_results(start_date: datetime.date, end_date: datetime.date) -> None:
    auth_url = "https://api.terna.it/transparency/oauth/accessToken"
    auth_token = auth_token_generator.AuthToken(auth_url).create_terna_request()
    print(auth_token)
    check_if_data_available_for(start_date)
    result = fetch_data(auth_token, start_date, end_date)
    if(result != None): 
        save_data(result)
    else:
        print("Authentication failed. Check your auth token.")



start_from = datetime.timedelta(days=int(sys.argv[1]))
check_for = datetime.timedelta(days=int(sys.argv[2]) - 1)
current_time = datetime.datetime.now().date()

get_results(current_time - start_from - check_for, current_time - start_from)
## give the start date and how many days to get data of as command line arguments