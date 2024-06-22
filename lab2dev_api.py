import os
import requests
import utils
from dotenv import load_dotenv

import browser_handler

load_dotenv()

class Lab2DevApi:
  _base_url = 'https://portal-api.lab2dev.com'
  _http_client: requests.Session

  def __init__(self):
    response = self.__get_cookie_response_from_user_and_password()

    self._http_client = requests.Session()
    self._http_client.cookies.update(response.cookies)

    utils.print_json(self.get("collaborators/whoami"))

  def __get_cookie_response_from_user_and_password(self):
    response = requests.post(
      "https://portal-api.lab2dev.com/auth/login/password",
      json={
        "email": os.environ['LAB2DEV_USER_EMAIL'],
        "password": os.environ['LAB2DEV_USER_PASSWORD'],
      },
      headers={
        "Origin": "https://apontamentos.lab2dev.com",
      }
    )

    return response

  def __get_cookie_response_from_web_app(self):
    portal_otp = browser_handler.get_portal_otp()

    print(f"OTP: {portal_otp}")

    response = requests.post(
      f'{self._base_url}/auth/verify-otp',
      json={
        'otp': portal_otp,
        'email': os.environ['LAB2DEV_USER_EMAIL'],
      },
    )

    return response

  def get(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.get(url)

    try: return response.json()
    except: return {}

  def post(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.post(url, json=data)

    try: return response.json()
    except: return {}

  def put(self, endpoint, data):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.put(url, json=data)

    try: return response.json()
    except: return {}

  def delete(self, endpoint):
    url = f'{self._base_url}/{endpoint}'
    response = self._http_client.delete(url)

    try: return response.json()
    except: return {}
