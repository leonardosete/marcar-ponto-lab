import os
import requests
from dotenv import load_dotenv

load_dotenv()

headers = {
  # TODO: You gotta be kidding me, find a way to generate this token, stupid
  'Authorization': f"Bearer {os.environ['LAB2DEV_API_TOKEN']}",
  'Content-Type': 'application/json'
}

base_url = 'https://portal-api.lab2dev.com'

def get(endpoint):
  url = f'{base_url}/{endpoint}'
  response = requests.get(url, headers=headers)
  return response.json()

def post(endpoint, data):
  url = f'{base_url}/{endpoint}'
  response = requests.post(url, json=data, headers=headers)
  return response.json()

def put(endpoint, data):
  url = f'{base_url}/{endpoint}'
  response = requests.put(url, json=data, headers=headers)
  return response.json()

def delete(endpoint):
  url = f'{base_url}/{endpoint}'
  response = requests.delete(url, headers=headers)
  return response.json()
