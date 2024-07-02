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


def getAssetTypes():
    response = requests.get(f"{API_BASE}/v2/asset-types", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get asset types failed")
        return None
    
def getAssets():
    response = requests.get(f"{API_BASE}/v2/assets", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get assets failed")
        return None
    
def getAsset(device_id):
    response = requests.get(f"{API_BASE}/v2/assets/{device_id}", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get asset failed: "+device_id)
        return None
    
def getAssetSensorData(device_id):
    response = requests.get(f"{API_BASE}/v2/assets/{device_id}/sensors", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get asset sensor data failed: "+device_id)
        return None
    
def getAssetsWithLocation():
    response = requests.get(f"{API_BASE}/v2/assets/recent-device-locations", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get assets with location failed")
        return None

def getDeviceData(device_id):
    response = requests.get(f"{API_BASE}/v2/device/{device_id}/data", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device data failed: "+device_id)
        return None

def getProjects():
    response = requests.get(f"{API_BASE}/v2/projects", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get projects failed")
        return None
    
def getProject(projectId):
    response = requests.get(f"{API_BASE}/v2/projects/{projectId}", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get project failed: "+projectId)
        return None
    
def getDevicesInProject(projectId):
    response = requests.get(f"{API_BASE}/v2/projects/{projectId}/devices", headers=common_headers)
    if response.status_code / 100 == 2:
        data = response.json()
        return data
    else: 
        print("Get device in project failed: "+projectId)
        return None
