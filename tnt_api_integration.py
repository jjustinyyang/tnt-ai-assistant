import json
import requests
from datetime import datetime, timedelta

# Load API configuration from a JSON file
with open("api.json", "r") as f:
    api = json.load(f)


common_headers = {}


def set_common_headers(idToken, xapikey):
    """
    Set common headers for API requests.

    Args:
    - idToken: The ID token for authentication.
    - xapikey: The client API key.
    """
    global common_headers
    common_headers = {
        "Authorization": idToken,
        "Origin": f"{api['base_url']}",
        "x-api-key": xapikey,
    }


def login(email, password):
    """
    Login to the API and return the authentication tokens.

    Args:
    - email: User's email.
    - password: User's password.

    Returns:
    - Tuple containing the ID token and the client API key, or (None, None) if login fails.
    """
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
            set_common_headers(
                login_response.json()["idToken"],
                login_response.json()["clientApiKey"]["clientId"],
            )
            return True
    except Exception as e:
        print(f"Exception: {str(e)}")
    print(f"Login failed: {login_response.text}")
    return False


def get_view_link(asset_id):
    """
    Generate a view link for the given asset ID.

    Args:
    - asset_id: The ID of the asset.

    Returns:
    - A string containing the view link.
    """
    return f"https://app.tagntrac.io/assets/{asset_id}"


def download(response):
    """
    Download the content of the response as a PDF file.

    Args:
    - response: The response object containing the PDF content.

    Returns:
    - A tuple containing the success status and a message.
    """
    if response:
        with open("report.pdf", "wb") as file:
            file.write(response.content)
        print("PDF downloaded successfully!")
        return True, "Report PDF generated successfully, ready to be downloaded."
    else:
        return (
            False,
            "Report PDF generation failed, no files available to be downloaded.",
        )


def call_tnt_api(function_name, id, query):
    """
    Call the Tag-N-Trac API and return the response.

    Args:
    - function_name: The name of the API function to call.
    - id: The ID to use in the API call (asset, device, or project ID).
    - query: The query string to append to the API endpoint.

    Returns:
    - The API response or None if the call fails.
    """
    if function_name in [
        "get_asset_sensor_data",
        "get_device_data",
        "get_device_events",
        "get_asset_pdf_report",
    ]:
        if id is None:
            print(f"{function_name} failed with missing endpoint argument: id")
            return None
        endpoint = api["endpoints"][function_name].format(id=id)
    else:
        endpoint = api["endpoints"][function_name]

    url = f"{api['base_url']}{endpoint}{query}"
    print(url)
    response = requests.get(url, headers=common_headers)

    if response.status_code // 100 == 2:
        print(f"{function_name} successful with status code {response.status_code}")
        return response
    else:
        print(f"{function_name} failed with status code {response.status_code}")
        return None


def get_asset_id_by_name(asset_name):
    """
    Get the asset ID by asset name.

    Args:
    - asset_name: The name of the asset.

    Returns:
    - The asset ID or None if not found.
    """
    asset = call_tnt_api("get_assets", None, f"?q={asset_name}")
    asset = asset.json()
    if asset and asset["assets"] and asset["assets"][0]:
        return asset["assets"][0]["id"]
    else:
        return None


def handle_query(function):
    """
    Handle the function query to determine the ID and query string.

    Args:
    - function: The function object containing the name and arguments.

    Returns:
    - A tuple containing the ID and query string.
    """
    function_name = function.name
    arguments = json.loads(function.arguments)

    id = None
    if function_name in [
        "get_asset_sensor_data",
        "get_visuals",
    ]:
        asset_name = arguments.get("asset_name", None)
        if asset_name:
            id = get_asset_id_by_name(asset_name)
            if id is None:
                print("Get asset id failed: " + asset_name)
        else:
            print("Get function argument failed: asset name")
    elif function_name in [
        "get_device_data",
        "get_device_events",
    ]:
        id = arguments.get("device_id", None)
        if id is None:
            print("Get function argument failed: device id")
    elif function_name == "get_asset_pdf_report":
        id = arguments.get("asset_name", None)
        if id is None:
            print("Get function argument failed: asset name")

    query = ""
    # special case: get_alerts api has to include blank queries
    if function_name == "get_alerts":
        query = "?parameter=&condition="
        page = arguments.get("page", "")
        limit = arguments.get("limit", "")
        proj = arguments.get("project", "")
        start = arguments.get("startDate", "")
        end = arguments.get("endDate", "")
        q = arguments.get("q", "")
        query += f"&page={page}&limit={limit}&project={proj}&startDate={start}&endDate={end}&q={q}"
    else:
        for key, value in arguments.items():
            if key not in ["asset_name", "device_id", "project_name"]:
                query += "&" if query else "?"
                query += f"{key}={value}"
    return id, query


def convert_time(format, time):
    """
    Convert the time from epoch or iso format to human-readable format.

    Args:
    - format: The format to convert the time to.
    - time: The time to convert.

    Returns:
    - The converted time.
    """
    match format:
        case "iso":
            time = datetime.fromisoformat(time.replace("Z", "+00:00"))
        case "epoch":
            time = datetime.fromtimestamp(int(time) // 1000)
        case "other":
            time = datetime.strptime(time.split(".")[0], "%Y-%m-%d %H:%M:%S")
        case _:
            return time
    offset = timedelta(hours=-7)
    time = (time + offset).strftime("%Y-%m-%d %H:%M:%S PDT")
    return time


def handle_response(function_name, api_response):
    """
    Handle the API response based on the function name.

    Args:
    - function_name: The name of the API function.
    - response: The API response object.

    Returns:
    - Handled response based on the function name.
    """
    if function_name == "get_asset_pdf_report":
        return download(api_response)
    if api_response is None:
        return None
    api_response = api_response.json()
    # print(api_response)
    handled_response = []
    match function_name:
        # specific cases require response handling here
        case "get_alerts":
            for alert in api_response["response"]:
                handled_response.append(
                    {
                        "Asset Name": alert["blegwId"],
                        "Device ID": alert["deviceId"],
                        "Condition": alert["value"],
                        "Triggered At": convert_time("iso", alert["updatedAt"]),
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Triggered At"], reverse=True
            )
            handled_response.append(api_response["pagination"])
        case "get_assets":
            for asset in api_response["assets"]:
                handled_response.append(
                    {
                        "Asset": asset["TrackedUnit"]["trackingId"],
                        "Tracked Unit": asset["TrackedUnit"]["tuType"],
                        "Device": asset["deviceId"],
                        "Device Type": asset["Device"]["deviceType"],
                        "Project": asset["Project"]["projectName"],
                        "Sensor Values": {
                            "Temperature": asset["lastReportedData"]["tm"],
                            "Humidity": asset["lastReportedData"]["h"],
                            "Pressure": asset["lastReportedData"]["prs"],
                            "Battery": asset["lastReportedData"]["batteryLeft"],
                        },
                        "Last Reported": convert_time("iso", asset["lastReportedAt"]),
                        "Alerts": asset["alerts"],
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Last Reported"], reverse=True
            )
            handled_response.append(api_response["pagination"])
        case "get_asset_sensor_data":
            for sensor_data in api_response:
                handled_response.append(
                    {
                        "Timestamp": convert_time("epoch", sensor_data["timestamp"]),
                        "Temperature": sensor_data["temperature"],
                        "Humidity": sensor_data["humidity"],
                        "Pressure": sensor_data["pressure"],
                        "Acceleration": {
                            "X": sensor_data["accX"],
                            "Y": sensor_data["accY"],
                            "Z": sensor_data["accZ"],
                        },
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Timestamp"], reverse=True
            )
        case "get_devices":
            for device in api_response["devices"]:
                handled_response.append(
                    {
                        "Device": device["id"],
                        "Device Type": device["deviceType"],
                        "Asset": (
                            {
                                "Asset Name": device["DeviceInfo"]["TrackedUnit"][
                                    "trackingId"
                                ],
                                "Tracking Unit": device["DeviceInfo"]["TrackedUnit"][
                                    "tuType"
                                ],
                            }
                            if device["DeviceInfo"]
                            else None
                        ),
                        "Project": (
                            device["DeviceInfo"]["Project"]["projectName"]
                            if device["DeviceInfo"]
                            else None
                        ),
                        "Status": "Deployed" if device["isActive"] else "In Stock",
                        "Last Modified": convert_time("iso", device["updatedAt"]),
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Last Modified"], reverse=True
            )
            handled_response.append(api_response["pagination"])
        case "get_device_data":
            if api_response["status"] != "SUCCESS":
                return None
            for device_data in api_response["response"]:
                handled_response.append(
                    {
                        "Timestamp": convert_time("epoch", device_data["ts"]),
                        "Location": {
                            "Latitude": device_data["lat"],
                            "Longitude": device_data["lng"],
                        },
                        "Temperature": device_data["tm"],
                        "Humidity": device_data["h"],
                        "Pressure": device_data["prs"],
                        "Acceleration": {
                            "X": device_data["accX"],
                            "Y": device_data["accY"],
                            "Z": device_data["accZ"],
                        },
                        "Events": device_data["evnts"],
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Timestamp"], reverse=True
            )
        case "get_device_events":
            if api_response["status"] != "SUCCESS":
                return None
            for event, values in api_response["events"].items():
                if event != "timestamp":
                    time_indices = [
                        index for index, value in enumerate(values) if value
                    ]
                    for index in time_indices:
                        handled_response.append(
                            {
                                "Timestamp": convert_time(
                                    "other", api_response["events"]["timestamp"][index]
                                ),
                                "Event": event,
                            }
                        )
            handled_response = sorted(
                handled_response, key=lambda x: x["Timestamp"], reverse=True
            )
        case "get_projects":
            for project in api_response:
                handled_response.append(
                    {
                        "Project Name": project["projectName"],
                        "Asset Count": len(project["DeviceInfos"]),
                        "Location": project["ShippingInfo"]["destinationAddress"][
                            "locality"
                        ],
                        "Last Modified": convert_time("iso", project["updatedAt"]),
                    }
                )
            handled_response = sorted(
                handled_response, key=lambda x: x["Last Modified"], reverse=True
            )
        case _:
            handled_response = api_response
    # print(handled_response)
    return handled_response


def get_function_output(function):
    """
    Get the output for the specified function.

    Args:
    - function: The function object containing the name and arguments.

    Returns:
    - The output of the function call.
    """
    function_name = function.name
    id, query = handle_query(function)
    print(f"function_name: {function_name}, id: {id}, query: {query}")
    if function_name == "get_visuals":
        if id:
            return get_view_link(id)
        else:
            return None
    api_response = call_tnt_api(function_name, id, query)
    return handle_response(function_name, api_response)
