import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AuthToken:

    base_url = None
    client_id = None
    client_secret = None
    auth_token = None
    expiry_time = None

    def __init__(self, base_url):
        self.base_url = base_url


    def send_request(self, url:str, client_token, headers) -> dict:
        response = requests.post(url, data=client_token, headers=headers)
        return response.json()
    

    def create_terna_request(self):
        self.client_id = os.getenv("terna_client_id")
        self.client_secret = os.getenv("terna_client_secret")


        client_token = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token = self.send_request(self.base_url, client_token, headers)
        self.auth_token = token['access_token']
        return self.auth_token


