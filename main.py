import os
import requests
import utils
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Lab2DevApi:
    _base_url = 'https://portal-api.lab2dev.com'
    _http_client: requests.Session

    def __init__(self):
        response = self.__get_cookie_response_from_user_and_password()
        self._http_client = requests.Session()
        self._http_client.cookies.update(response.cookies)

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
            return []

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
    default_description = os.getenv('DESCRIPTION', 'Atividades SRE/DevOps')
    overwrite_existing = os.getenv('OVERWRITE_EXISTING', 'false').lower() == 'true'
    
    lab2dev_projects = lab2dev_api.get('projects')

    sre_project = list(filter(
        lambda project: (project['name'] == project_name), 
        lab2dev_projects,
    ))[0]

    start_date_str = os.getenv('START_DATE', '')
    end_date_str = os.getenv('END_DATE', '')

    if not start_date_str or not end_date_str:
        print("❌ Datas de início e fim são obrigatórias.")
        return

    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

    if start_date > end_date:
        print("❌ A data de início não pode ser maior que a data de fim.")
        return

    work_start_time = os.getenv('WORK_START_TIME', '09:00:00')
    work_end_time = os.getenv('WORK_END_TIME', '17:00:00')

    # Obtendo a lista de feriados via API
    non_working_days = lab2dev_api.get('tracker/workdays')

    formatted_non_working_days = list([
        day['date'][:10]
        for day in non_working_days 
        if isinstance(day, dict) and day.get('type') == 'NON_WORKING_DAY'
    ])

    existing_appointments = lab2dev_api.get('appointments')
    existing_dates = {appt['date'][:10]: appt['id'] for appt in existing_appointments if isinstance(appt, dict) and 'date' in appt and 'id' in appt}

    current_date = start_date
    while current_date <= end_date:
        short_format_date = current_date.strftime('%Y-%m-%d')

        if current_date.weekday() in [5, 6]:
            print(f'❌ {current_date.strftime("%d/%m/%Y")} é fim de semana. Pulando.')
            current_date += timedelta(days=1)
            continue

        if short_format_date in formatted_non_working_days:
            print(f'❌ {current_date.strftime("%d/%m/%Y")} é feriado. Pulando.')
            current_date += timedelta(days=1)
            continue

        formatted_date = current_date.strftime('%Y-%m-%dT03:00:00.000Z')
        start_datetime = f"{current_date.strftime('%Y-%m-%d')}T{work_start_time}.000Z"
        end_datetime = f"{current_date.strftime('%Y-%m-%d')}T{work_end_time}.000Z"

        if short_format_date in existing_dates:
            if overwrite_existing:
                print(f'🔄 Atualizando apontamento existente para {current_date.strftime("%d/%m/%Y")}')
                appointment_id = existing_dates[short_format_date]
                lab2dev_api.put(f'appointments/{appointment_id}', {
                    'start': start_datetime,
                    'end': end_datetime,
                    'title': default_description,
                })
            else:
                print(f'🔹 {current_date.strftime("%d/%m/%Y")} já tem um apontamento registrado. Pulando.')
        else:
            appointment = {
                'date': formatted_date,
                'start': start_datetime,
                'end': end_datetime,
                'billable': True,
                'extra': False,
                'title': default_description,
                'project': sre_project['id'],
            }
            appointment_response = lab2dev_api.post('appointments', appointment)

            if 'error' in appointment_response:
                print(f'❌ Erro ao registrar o ponto para {current_date.strftime("%d/%m/%Y")}')
            else:
                print(f'✅ Ponto registrado para {current_date.strftime("%d/%m/%Y")}')

        current_date += timedelta(days=1)

if __name__ == "__main__":
    register_appointments()
