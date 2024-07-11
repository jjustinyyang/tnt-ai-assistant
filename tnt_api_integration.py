from datetime import datetime, timezone
import requests
import json


with open('api.json', 'r') as f:
    api = json.load(f)


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
    login_response = requests.post(f"{api['base_url']}/login?clientId=Tbocs0cjhrac",
                             data = json.dumps({"emailId" : email, "userSecret" : password,"reqType": "cognitoAuth"}),
                             headers={"Content-Type" : "application/json", "Origin" : "DOC.API"})
    try:
        if login_response.json()["status"] == "SUCCESS":
            print("Login successful as:", email)
            return (login_response.json()["idToken"], login_response.json()['clientApiKey']['clientId'])
    except Exception as e:
        print(f"Exception: {str(e)}")
    print(f"Login failed: {login_response.text}")
    return (None, None)

# Capture user input for login
id, pwd = prompt()
# login
idToken, xapikey = login(id, pwd)
common_headers = {"Authorization" : idToken,
                  "Origin" : f"{api['base_url']}",
                  "x-api-key" : xapikey}


def call_api(function_name, id, query):
    if function_name in ["get_asset", "get_asset_alerts", "get_asset_sensor_data"]:
        endpoint = api["endpoints"][function_name].format(asset_id=id)
    elif function_name in ["get_device_data", "get_device_event_data", "get_device_location_data", "get_device_acceleration_data"]:
        endpoint = api["endpoints"][function_name].format(device_id=id)
    elif function_name in ["get_project", "get_devices_in_project"]:
        endpoint = api["endpoints"][function_name].format(project_id=id)
    else:
        endpoint = api["endpoints"][function_name]

    url = f"{api['base_url']}{endpoint}{query}"
    print(url)
    response = requests.get(url, headers=common_headers)
    
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else:
        print(f"{function_name} failed with status code {response.status_code}")
        return None

def get_function_output(function):
    function_name = function.name
    arguments = json.loads(function.arguments)

    id = ""
    if function_name in ["get_asset", "get_asset_alerts", "get_asset_sensor_data"]:
        asset_name = arguments.get("asset_name", "")
        asset = call_api("get_assets", "", f"?q={asset_name}")
        if not asset:
            print("Get asset id failed: " + asset_name)
            return ""
        if not asset["assets"]:
            print("No asset found: " + asset_name)
            return ""
        id = asset["assets"][0]["id"]
    elif function_name in ["get_device_data", "get_device_event_data", "get_device_location_data", "get_device_acceleration_data"]:
        device_id = arguments.get("device_id", "")
        id = device_id
    elif function_name in ["get_project", "get_devices_in_project"]:
        project_name = arguments.get("project_name", "")
        projects = call_api("get_projects", "", "")
        if not projects:
            return ""
        projects = projects["projects"]
        for project in projects:
            if project["projectName"] == project_name or project["shortName"] == project_name:
                id = project["id"]
                break
        if not id:
            print("Get project id failed: " + project_name)
            return ""

    query = "?"
    for key, value in arguments.items():
        if key not in ["asset_name", "device_id", "project_name"]:
            query += f"{key}={value}&"

    print(f"function_name: {function_name}, id: {id}, query: {query}")
    return call_api(function_name, id, query)
