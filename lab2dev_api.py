import os
import json
import requests
from dotenv import load_dotenv

import browser_handler

load_dotenv()

class Lab2DevApi:
  _base_url = 'https://portal-api.lab2dev.com'
  _http_client: requests.Session

  def __init__(self):
    portal_otp = browser_handler.get_portal_otp()

    response = requests.post(
      f'{self._base_url}/auth/verify-otp',
      json={
        'otp': portal_otp,
        'email': os.environ['LAB2DEV_USER_EMAIL'],
      },
    )

    self._http_client = requests.Session()
    self._http_client.cookies.update(response.cookies)

  def get(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.get(url)
    return response.json()

  def post(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.post(url, json=data)
    return response.json()

  def put(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.put(url, json=data)
    return response.json()

  def delete(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.delete(url)
    return response.json()
