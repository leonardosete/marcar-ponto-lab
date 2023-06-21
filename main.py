from datetime import datetime, timedelta

import utils
import clockify_api

workspace_name = 'Lab2dev'
project_name = 'Alocação IT Eng - SRE - T&M'
default_description = 'Whirlpool - Automated'

workspaces = clockify_api.get("/v1/workspaces")

lab2dev_workspace = list(filter(
  lambda workspace: (workspace['name'] == workspace_name), 
  workspaces,
))[0]

lab2dev_projects = clockify_api.get(
  f'/v1/workspaces/{lab2dev_workspace["id"]}/projects'
)

sre_project = list(filter(
  lambda project: (project['name'] == project_name), 
  lab2dev_projects,
))[0]

today = datetime.today()
next_date = datetime(today.year, today.month, 1)

while next_date.month == today.month:
  current_date = next_date
  next_date += timedelta(days=1)

  if current_date.weekday() in [5, 6]:
    continue

  start_date = current_date.strftime("%Y-%m-%dT12:00:00.%fZ")
  end_date = current_date.strftime("%Y-%m-%dT20:00:00.%fZ")

  time_entry = {
    "start": start_date,
    "end": end_date,
    "billable": True,
    "description": default_description,
    "projectId": sre_project['id'],
    "tagIds": None,
    "taskId": None,
    "customFields": [],
    "customAttributes": [],
  }

  add_time_entry_response = clockify_api.post(
    f"/v1/workspaces/{lab2dev_workspace['id']}/time-entries",
    time_entry,
  )

  if "error" in add_time_entry_response:
    print(f"❌ day {current_date}")
    
    utils.print_json({
      "request": time_entry,
      "response": add_time_entry_response,
    })
  else:
    print(f"✅ day {current_date}")
