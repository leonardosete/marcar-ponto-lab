import os
import requests
from dotenv import load_dotenv

load_dotenv()

headers = {
  'X-Api-Key': os.environ['CLOCKIFY_API_KEY'],
  'Content-Type': 'application/json'
}

base_url = 'https://api.clockify.me/api'

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
