import time
import json
import gradio as gr
from openai import OpenAI

from api_calls import call_api


def get_function_output(function):
    function_name = function.name
    arguments = json.loads(function.arguments)
    id = ""
    query = ""
    match function_name:
        case "get_alerts":
            page = arguments.get("page", "1")
            limit = arguments.get("limit", "50")
            parameter = arguments.get("parameter", "")
            condition = arguments.get("condition", "")
            project = arguments.get("project", "")
            startDate = arguments.get("startDate", "")
            endDate = arguments.get("endDate", "")
            q = arguments.get("q", "")
            query = f"?page={page}&limit={limit}&parameter={parameter}&condition={condition}&project={project}&startDate={startDate}&endDate={endDate}&q={q}"
        case "get_asset_types":
            pass
        case "get_assets":
            page = arguments.get("page", "1")
            limit = arguments.get("limit", "50")
            deviceType = arguments.get("deviceType", "")
            assetType = arguments.get("assetType", "")
            project = arguments.get("project", "")
            q = arguments.get("q", "")
            startDate = arguments.get("startDate", "")
            endDate = arguments.get("endDate", "")
            query = f"?page={page}&limit={limit}&deviceType={deviceType}&assetType={assetType}&project={project}&q={q}&startDate={startDate}&endDate={endDate}"
        case "get_asset":
            asset_name = arguments.get("asset_name", "")
            asset = call_api("get_assets", "", f"?q={asset_name}")
            if not asset:
                print("Get asset id failed: "+asset_name)
                return ""
            id = asset["assets"][0]["id"]
        case "get_asset_alerts":
            asset_name = arguments.get("asset_name", "")
            page = arguments.get("page", "1")
            limit = arguments.get("limit", "50")
            query = f"?page={page}&limit={limit}"
            asset = call_api("get_assets", "", f"?q={asset_name}")
            if not asset:
                print("Get asset id failed: "+asset_name)
                return ""
            id = asset["assets"][0]["id"]
        case "get_asset_sensor_data":
            asset_name = arguments.get("asset_name", "")
            timePeriod = arguments.get("timePeriod", "")
            binInterval = arguments.get("binInterval", "")
            query = f"?timePeriod={timePeriod}&binInterval={binInterval}"
            asset = call_api("get_assets", "", f"?q={asset_name}")
            if not asset:
                print("Get asset id failed: "+asset_name)
                return ""
            id = asset["assets"][0]["id"]
        case "get_assets_with_location":
            pass
        case "get_devices":
            page = arguments.get("page", "1")
            limit = arguments.get("limit", "50")
            deviceType = arguments.get("deviceType", "")
            provisioned = arguments.get("provisioned", "")
            project = arguments.get("project", "")
            q = arguments.get("q", "")
            query = f"?page={page}&limit={limit}&deviceType={deviceType}&provisioned={provisioned}&project={project}&q={q}"
        case "get_device_data":
            id = arguments.get("device_id", "")
            startDate = arguments.get("startDate", "")
            endDate = arguments.get("endDate", "")
            query = f"?start={startDate}&end={endDate}"
        case "get_device_event_data":
            id = arguments.get("device_id", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
        case "get_device_location_data":
            id = arguments.get("device_id", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
        case "get_device_acceleration_data":
            id = arguments.get("device_id", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
        case "get_projects":
            pass
        case "get_project":
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
                print("Get project id failed: "+project_name)
                return ""
        case "get_devices_in_project":
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
                print("Get project id failed: "+project_name)
                return ""
    print(f"function_name: {function_name}, id: {id}, query: {query}")
    return call_api(function_name, id, query)


client = OpenAI(api_key='sk-proj-VIa0xmeWs7LG6lyHmleST3BlbkFJLyhuWf28HAXT88QhN25M', organization='org-qRa4NGJi0VworFbpu3ymwscd')

assistant = client.beta.assistants.create(
    name="TNT AI Assistant",
    instructions = '''
        You are a helpful assistant that retrieves information for the user.

        You will identify what information the user wants by parsing user queries and extracting relevant parameters, and call the function with the corresponding arguments to get information. You can ask the user to provide any missing parameters required for the function call.

        If you are unsure about the user's request, ask to clarify. If you are unable to help, gracefully reject their request.

        Some rules to follow:
        - Our server stores timestamps in unix form, convert between unix and human-readable to interact with the user. Always convert unix timestamps received from function calls to human-readable date and time format to display to the user.
        - Show up to 8 results, indicate to the user if there are more than 8.
        - The user is in PDT time zone.
        ''',
    model="gpt-3.5-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_alerts",
                "description": "Get information of alerts user requested",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The number of pages displaying to the user",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of rows of alerts displaying to the user per page",
                        },
                        "parameter": {
                            "type": "string",
                            "description": ""
                        },
                        "condition": {
                            "type": "string",
                            "description": ""
                        },
                        "project": {
                            "type": "string",
                            "description": "The name of the project which user filters out assets by",
                        },
                        "q": {
                            "type": "string",
                            "description": "The name of the asset or ID of the device user search by",
                        },
                        "startDate": {
                            "type": "string",
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to filter assets"
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to filter assets"
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset_types",
                "description": "Get information of asset types",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_assets",
                "description": "Get information of assets user requested",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The number of pages displaying to the user",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of rows of assets displaying to the user per page",
                        },
                        "deviceType": {
                            "type": "string",
                            "description": "The type of device the user filters for: use BLE_TAG for bluetooth, CATM1_TAG for cellular, NFC_TAG for NFC",
                        },
                        "assetType": {
                            "type": "string",
                            "description": "The type of asset the user filters for: use UNIT for unit, BOX for box, PALLET for pallet, CONTAINER for container",
                        },
                        "project": {
                            "type": "string",
                            "description": "The name of the project which user filters out assets by",
                        },
                        "q": {
                            "type": "string",
                            "description": "The name of the asset or ID of the device user search by",
                        },
                        "startDate": {
                            "type": "string",
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to filter assets"
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to filter assets"
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset",
                "description": "Get information of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset_alerts",
                "description": "Get information of alerts of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset",
                        },
                        "page": {
                            "type": "string",
                            "description": "The number of pages displaying to the user",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of rows of asset alerts displaying to the user per page",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset_sensor_data",
                "description": "Get sensor data of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                        "binInterval": {
                            "type": "string",
                            "description": "The time interval that user wants the data in. e.g. bin interval is 15 if user wants data in every 15 minutes",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_assets_with_location",
                "description": "Get information of assets with their locations",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_devices",
                "description": "Get information of devices user requested",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The number of pages displaying to the user",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of rows of devices displaying to the user per page",
                        },
                        "deviceType": {
                            "type": "string",
                            "description": "The type of device the user filters for: use BLE_TAG for bluetooth, CATM1_TAG for cellular, NFC_TAG for NFC",
                        },
                        "provisioned": {
                            "type": "string",
                            "description": "The status of the device: deployed or in stock. Set provisioned to true if deployed, false if in stock",
                        },
                        "project": {
                            "type": "string",
                            "description": "The ID of the project which user filters out assets by",
                        },
                        "q": {
                            "type": "string",
                            "description": "The ID of the asset or ID of the device user search by",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_data",
                "description": "Get general data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "startDate": {
                            "type": "string",
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to retrieve device data"
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to retrieve device data"
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_event_data",
                "description": "Get event data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_location_data",
                "description": "Get location data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_acceleration_data",
                "description": "Get acceleration data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_projects",
                "description": "Get information of projects",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project",
                "description": "Get information of a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project",
                        }
                    },
                    "required": ["project_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_devices_in_project",
                "description": "Get information of devices in a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project",
                        }
                    },
                    "required": ["project_name"],
                },
            },
        },
    ],
)


thread = client.beta.threads.create()

def chatbot(user_input, chat_history):
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    while run.status not in ["completed", "failed", "requires_action"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print("responding to user input "+run.status)
    while (run.status == "requires_action"):
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            print(tool_call.function)
            function_output = json.dumps(get_function_output(tool_call.function))
            print(function_output)
            tool_outputs.append({"tool_call_id": tool_call.id, "output": function_output})
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        while run.status not in ["completed", "failed", "requires_action"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print("function submission "+run.status)
    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
    print(messages)
    return messages[0].content[0].text.value

if __name__ == "__main__":
    gr.ChatInterface(
        chatbot,
        title="Tag-N-Trac AI Assistant",
        chatbot=gr.Chatbot(
            value=[[None, "Hi, how can I help you?"]],
            height="70vh",
            show_copy_button=True,
            likeable=True,
            avatar_images=[
                "https://t3.ftcdn.net/jpg/05/53/79/60/360_F_553796090_XHrE6R9jwmBJUMo9HKl41hyHJ5gqt9oz.jpg",
                "https://mms.businesswire.com/media/20220125006080/en/1338748/22/Tag-N-Trac.jpg"
            ]
        ),
    ).launch(share=True)
