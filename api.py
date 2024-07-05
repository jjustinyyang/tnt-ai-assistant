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


# api functions
def getAssetTypes():
    response = requests.get(f"{API_BASE}/v2/asset-types", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get asset types failed")
        return None
    
def getAssets(query):
    response = requests.get(f"{API_BASE}/v2/assets"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get assets failed")
        return None
    
def getAsset(asset_name):
    asset = getAssets(f"?q={asset_name}")
    if asset:
        asset_id = asset["assets"][0]["id"]
        print(asset_id)
        response = requests.get(f"{API_BASE}/v2/assets/{asset_id}", headers=common_headers)
        if response.status_code / 100 == 2:
            data = response.json()
            return data
        else: 
            print("Get asset failed: "+asset_name)
            return None
    else:
        print("Get asset id failed: "+asset_name)
        return None
    
def getAssetSensorData(asset_name, query):
    asset = getAssets(f"?q={asset_name}")
    if asset:
        asset_id = asset["assets"][0]["id"]
        response = requests.get(f"{API_BASE}/v2/assets/{asset_id}/sensors"+query, headers=common_headers)
        if response.status_code / 100 == 2:
            data = response.json()
            return data
        else: 
            print("Get asset sensor data failed: "+asset_name)
            return None
    else:
        print("Get asset id failed: "+asset_name)
        return None
    
def getAssetsWithLocation():
    response = requests.get(f"{API_BASE}/v2/assets/recent-device-locations", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get assets with location failed")
        return None

def getDevices(query):
    response = requests.get(f"{API_BASE}/v2/devices"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get devices failed")
        return None
    
def getDeviceData(device_id, query):
    response = requests.get(f"{API_BASE}/v2/device/{device_id}/data"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device data failed: "+device_id)
        return None
    
def getDeviceEventData(device_id, query):
    response = requests.get(f"{API_BASE}/v2/device/{device_id}/eventData"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device event data failed: "+device_id)
        return None

def getDeviceLocationData(device_id, query):
    response = requests.get(f"{API_BASE}/v2/device/{device_id}/locationData"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device location data failed: "+device_id)
        return None

def getDeviceAccelerationData(device_id, query):
    response = requests.get(f"{API_BASE}/v2/device/{device_id}/accData"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device acceleration data failed: "+device_id)
        return None

# still buggy: getProjects might not have queryable objects seems like
def getProjects(query):
    response = requests.get(f"{API_BASE}/v2/projects"+query, headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get projects failed")
        return None
    
def getProject(project_name):
    project = getProjects(f"q={project_name}")
    if project:
        project_id = project["projects"][0]["id"]
        print(project_id)
        response = requests.get(f"{API_BASE}/v2/projects/{project_id}", headers=common_headers)
        if response.status_code / 100 == 2:
            data = response.json()
            return data
        else: 
            print("Get project failed: "+project_name)
            return None
    else:
        print("Get project id failed: "+project_name)
        return None
    
def getDevicesInProject(project_name):
    project = getProjects(f"q={project_name}")
    if project:
        project_id = project["projects"][0]["id"]
        response = requests.get(f"{API_BASE}/v2/projects/{project_id}/devices", headers=common_headers)
        if response.status_code / 100 == 2:
            data = response.json()
            return data
        else: 
            print("Get device in project failed: "+project_name)
            return None
    else:
        print("Get project id failed: "+project_name)
        return None
