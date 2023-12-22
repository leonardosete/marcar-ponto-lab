import os
import requests
from dotenv import load_dotenv

import browser_handler

load_dotenv()

class Lab2DevApi:
  _base_url = 'https://portal-api.lab2dev.com'

  _headers = {
    'Content-Type': 'application/json'
  }

  def __init__(self):
    access_token, _ = browser_handler.get_authorization_token()
    self._headers['Authorization'] = f'Bearer {access_token}'

  def get(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = requests.get(url, headers=self._headers)
    return response.json()

  def post(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = requests.post(url, json=data, headers=self._headers)
    return response.json()

  def put(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = requests.put(url, json=data, headers=self._headers)
    return response.json()

  def delete(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = requests.delete(url, headers=self._headers)
    return response.json()
