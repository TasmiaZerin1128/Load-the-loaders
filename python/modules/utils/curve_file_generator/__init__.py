import datetime
import os

class CurveGenerator:

    data = None

    def __init__(self, data):
        self.data = data

    def createCSV(self, folder_name):
        if not os.path.exists(f'curvefiles/{folder_name}'):
            os.makedirs(f'curvefiles/{folder_name}')

        csv_file = f'curvefiles/{folder_name}/first_loader_{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}.csv'
        self.data.to_csv(csv_file, index=False)
        print(f'File successfully created at {csv_file}')