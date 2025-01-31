import os
import requests
import utils
from datetime import datetime
from dotenv import load_dotenv

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

        if response.status_code != 200:
            raise Exception("Failed to authenticate. Check credentials.")

        return response

    def get(self, endpoint):
        url = f'{self._base_url}/{endpoint}'
        response = self._http_client.get(url)

        try:
            return response.json()
        except:
            return {}

    def post(self, endpoint, data):
        url = f'{self._base_url}/{endpoint}'
        response = self._http_client.post(url, json=data)

        try:
            return response.json()
        except:
            return {}

    def put(self, endpoint, data):
        url = f'{self._base_url}/{endpoint}'
        response = self._http_client.put(url, json=data)

        try:
            return response.json()
        except:
            return {}

    def delete(self, endpoint):
        url = f'{self._base_url}/{endpoint}'
        response = self._http_client.delete(url)

        try:
            return response.json()
        except:
            return {}

def register_appointments():
    lab2dev_api = Lab2DevApi()

    project_name = 'WHP TM - SRE Sênior'
    default_description = 'Atividades SRE/DevOps'

    lab2dev_projects = lab2dev_api.get('projects')

    sre_project = list(filter(
        lambda project: (project['name'] == project_name), 
        lab2dev_projects['projects'],
    ))[0]

    today = datetime.today()
    short_format_today = today.strftime('%Y-%m-%d')

    # Obtendo os horários da variável de ambiente (ou usando padrão)
    start_time = os.getenv('START_DATE', '09:00:00')
    end_time = os.getenv('END_DATE', '17:00:00')

    formatted_date = today.strftime('%Y-%m-%dT03:00:00.000Z')
    start_date = f"{today.strftime('%Y-%m-%d')}T{start_time}.000Z"
    end_date = f"{today.strftime('%Y-%m-%d')}T{end_time}.000Z"

    appointment = {
        'date': formatted_date,
        'start': start_date,
        'end': end_date,
        'billable': True,
        'extra': False,
        'title': default_description,
        'project': sre_project['id'],
    }

    appointment_response = lab2dev_api.post('appointments', appointment)

    if 'error' in appointment_response:
        print(f'❌ Erro ao registrar o ponto de hoje ({short_format_today})')
    else:
        print(f'✅ Ponto registrado para hoje ({short_format_today})')

if __name__ == "__main__":
    register_appointments()
