from datetime import datetime, timezone
import requests
import json

# login
API_BASE = "https://api.tagntrac.io"

# Placeholder variables for user credentials and filename
id = "username" 
pwd = "password" 
def prompt():
    """Prompt user for username, password, and file name for device id list."""
    # id = input("Enter username: ")
    # pwd = input("Enter password: ")
    id = "justin.yang@tagntrac.com"
    pwd = "Chenglin0312."
    return id, pwd

def login(email, password):
    login_response = requests.post(f"{API_BASE}/login?clientId=Tbocs0cjhrac",
                             data = json.dumps({"emailId" : email, "userSecret" : password,"reqType": "cognitoAuth"}),
                             headers={"Content-Type" : "application/json", "Origin" : "DOC.API"})
    try:
        if login_response.json()["status"] == "SUCCESS":
            print("Login successful as ", email)
            return (login_response.json()["idToken"], login_response.json()['clientApiKey']['clientId'])
    except Exception as e:
        print(f"Exception: {str(e)}")
    print(f"Login failed: {login_response.text}")
    return (None, None)

# Capture user input
id, pwd = prompt()

idToken, xapikey = login(id, pwd)
common_headers = {"Authorization" : idToken,
                  "Origin" : f"{API_BASE}",
                  "x-api-key" : xapikey}


with open('api.json', 'r') as f:
    api = json.load(f)

def call_api(function_name, id, query):
    if function_name in ["get_asset", "get_asset_sensor_data"]:
        endpoint = api["endpoints"][function_name].format(asset_id=id)
    elif function_name in ["get_device_data", "get_device_event_data", "get_device_location_data", "get_device_acceleration_data"]:
        endpoint = api["endpoints"][function_name].format(device_id=id)
    elif function_name in ["get_project", "get_devices_in_project"]:
        endpoint = api["endpoints"][function_name].format(project_id=id)
    else:
        endpoint = api["endpoints"][function_name]

    url = f"{api['base_url']}{endpoint}{query}"
    response = requests.get(url, headers=common_headers)
    
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else:
        print(f"{function_name} failed with status code {response.status_code}")
        return None
