from datetime import datetime, timezone
import requests
import json


with open("api.json", "r") as f:
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
    login_response = requests.post(
        f"{api['base_url']}/login?clientId=Tbocs0cjhrac",
        data=json.dumps(
            {"emailId": email, "userSecret": password, "reqType": "cognitoAuth"}
        ),
        headers={"Content-Type": "application/json", "Origin": "DOC.API"},
    )
    try:
        if login_response.json()["status"] == "SUCCESS":
            print("Login successful as:", email)
            return (
                login_response.json()["idToken"],
                login_response.json()["clientApiKey"]["clientId"],
            )
    except Exception as e:
        print(f"Exception: {str(e)}")
    print(f"Login failed: {login_response.text}")
    return (None, None)


# Capture user input for login
id, pwd = prompt()
# login
idToken, xapikey = login(id, pwd)
common_headers = {
    "Authorization": idToken,
    "Origin": f"{api['base_url']}",
    "x-api-key": xapikey,
}


def download(response):
    with open("device_info.pdf", "wb") as file:
        file.write(response.content)
    print("PDF downloaded successfully!")


def call_tnt_api(function_name, id, query):
    if function_name in ["get_asset", "get_asset_alerts", "get_asset_sensor_data"]:
        if not id:
            print("Get function argument failed: asset id")
            return None
        endpoint = api["endpoints"][function_name].format(asset_id=id)
    elif function_name in [
        "get_device_data",
        "get_device_event_data",
        "get_device_location_data",
        "get_device_acceleration_data",
        "get_device_pdf",
    ]:
        if not id:
            print("Get function argument failed: device id")
            return None
        endpoint = api["endpoints"][function_name].format(device_id=id)
    elif function_name in ["get_project", "get_devices_in_project"]:
        if not id:
            print("Get function argument failed: project id")
            return None
        endpoint = api["endpoints"][function_name].format(project_id=id)
    else:
        endpoint = api["endpoints"][function_name]

    url = f"{api['base_url']}{endpoint}{query}"
    print(url)
    response = requests.get(url, headers=common_headers)

    if response.status_code / 100 == 2:
        if function_name == "get_device_pdf":
            download(response)
            return True, "Report PDF generated successfully, ready to be downloaded."
        return response.json()
    else:
        print(f"{function_name} failed with status code {response.status_code}")
        if function_name == "get_device_pdf":
            return (
                False,
                "Report PDF generation failed, no files available to be downloaded.",
            )
        return None


def get_asset_id_by_name(asset_name):
    asset = call_tnt_api("get_assets", None, f"?q={asset_name}")
    if asset and asset["assets"] and asset["assets"][0]:
        return asset["assets"][0]["id"]
    else:
        return None


def get_project_id_by_name(project_name):
    projects = call_tnt_api("get_projects", None, "")
    if projects and projects["projects"]:
        projects = projects["projects"]
        for project in projects:
            if (
                project["projectName"] == project_name
                or project["shortName"] == project_name
            ):
                return project["id"]
    return None


def handle_query(function):
    function_name = function.name
    arguments = json.loads(function.arguments)

    id = None
    if function_name in ["get_asset", "get_asset_alerts", "get_asset_sensor_data"]:
        asset_name = arguments.get("asset_name", None)
        if asset_name:
            id = get_asset_id_by_name(asset_name)
            if not id:
                print("Get asset id failed: " + asset_name)
        else:
            print("Get function argument failed: asset name")
    elif function_name in [
        "get_device_data",
        "get_device_event_data",
        "get_device_location_data",
        "get_device_acceleration_data",
        "get_device_pdf",
    ]:
        id = arguments.get("device_id", None)
        if not id:
            print("Get function argument failed: device id")
    elif function_name in ["get_project", "get_devices_in_project"]:
        project_name = arguments.get("project_name", None)
        if project_name:
            id = get_project_id_by_name(project_name)
            if not id:
                print("Get project id failed: " + project_name)
        else:
            print("Get function argument failed: project name")

    query = ""
    for key, value in arguments.items():
        if key not in ["asset_name", "device_id", "project_name"]:
            query += "?" if not query else "&"
            query += f"{key}={value}"
    return id, query


def get_function_output(function):
    function_name = function.name
    id, query = handle_query(function)
    print(f"function_name: {function_name}, id: {id}, query: {query}")
    return call_tnt_api(function_name, id, query)
