import datetime
import re
from more_itertools import first
import requests
from bs4 import BeautifulSoup
import sys
from modules.utils import auth_token_generator, curve_file_generator

CZC_Table_Map = [
    'date',
    'hour',
    'bg,price,euro/mwh',
    'gr,price,euro/mwh',
    'bg,gr,atc,euro/mwh',
    'gr,bg,atc,euro/mwh',
    'bg,gr,crossborderflow,euro/mwh',
    'gr,bg,crossborderflow,euro/mwh'
]

BGRO_CZC_Table_Map = [
    'date',
    'hour',
    'bg,price,euro/mwh',
    'ro,price,euro/mwh',
    'bg,ro,atc,euro/mwh',
    'ro,bg,atc,euro/mwh',
    'bg,ro,crossborderflow,euro/mwh',
    'ro,bg,crossborderflow,euro/mwh'
]


def check_if_data_available_for(start_date: datetime.date):
    if start_date < datetime.date(year=2024, month=1, day=24):
        raise ValueError(f"{start_date} is prior to the data publish start date of January 24th, 2024.")
    if start_date > datetime.datetime.now().date() + datetime.timedelta(days=1):
        raise ValueError(f"{start_date} is in the future. Query date is supported till today's date.")

def map_table_data(table: list, Table_Map: list):
    table_data = []
    for row in table[1:]:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        row_data = dict(zip(Table_Map, cols))
        table_data.append(row_data)
        #print(table_data)
    
    return table_data


def save_data(data: list):
    all_data = []
    rows_in_table_one = data[0].find_all('tr')
    rows_in_table_two = data[1].find_all('tr')

    data_table_one = map_table_data(rows_in_table_one, CZC_Table_Map)
    data_table_two = map_table_data(rows_in_table_two, BGRO_CZC_Table_Map)

    merged_data = [{**d1, **d2} for d1, d2 in zip(data_table_one, data_table_two)]
    for row in merged_data:
        for key in row:
            new_data = {}
            if key not in ['date', 'hour']:
                new_data['date'] = f"{row['date']} {row['hour'].zfill(2)}:00"
                new_data['value'] = row[key]
                new_data['keys'] = key
                new_data['name'] = 'ibex_bam_report'
                all_data.append(new_data)

    generator = curve_file_generator.CurveGenerator(all_data)
    generator.createCSV('ibex_bam_report')

def fetch_data(given_date: datetime.date):
    print('Fetching data')
    data_url = "https://ibex.bg/markets/dam/cross-zonal-capacities/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }

    form_data = {
        'fromDate': given_date,
        'but_search': 'Search'
    }

    req = requests.Session()
    response = req.post(data_url, headers=headers, data=form_data)
    if response.status_code != 200 : raise Exception("Request failed.")

    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    #Two hidden tables - czc-table, bgro-czc-table to fetch
    first_table = soup.find('table', {'class':'czc-table'})
    second_table = soup.find('table', {'class':'bgro-czc-table'})

    data.append(first_table)
    data.append(second_table)
    return data


def get_results(given_date: datetime.date) -> None:
    check_if_data_available_for(given_date)
    data = fetch_data(given_date)
    save_data(data)

get_results(datetime.datetime.now().date() - datetime.timedelta(days=int(sys.argv[1])))