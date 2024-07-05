import time
import json
import gradio as gr
from openai import OpenAI

from api import getAssetTypes, getAssets, getAsset, getAssetSensorData, getAssetsWithLocation, getDevices, getDeviceData, getDeviceEventData, getDeviceLocationData, getDeviceAccelerationData, getProjects, getProject, getDevicesInProject


def get_function_output(function):
    arguments = json.loads(function.arguments)
    match function.name:
        case "getAssetTypes":
            return getAssetTypes()
        case "getAssets":
            page = arguments.get("page", "")
            limit = arguments.get("limit", "")
            deviceType = arguments.get("deviceType", "")
            assetType = arguments.get("assetType", "")
            project = arguments.get("project", "")
            q = arguments.get("q", "")
            startDate = arguments.get("startDate", "")
            endDate = arguments.get("endDate", "")
            query = f"?page={page}&limit={limit}&deviceType={deviceType}&assetType={assetType}&project={project}&q={q}&startDate={startDate}&endDate={endDate}"
            print(query)
            return getAssets(query)
        case "getAsset":
            assetName = arguments.get("assetName", "")
            return getAsset(assetName)
        case "getAssetSensorData":
            assetName = arguments.get("assetName", "")
            timePeriod = arguments.get("timePeriod", "")
            binInterval = arguments.get("binInterval", "")
            query = f"?timePeriod={timePeriod}&binInterval={binInterval}"
            print(query)
            return getAssetSensorData(assetName, query)
        case "getAssetsWithLocation":
            return getAssetsWithLocation()
        case "getDevices":
            page = arguments.get("page", "")
            limit = arguments.get("limit", "")
            deviceType = arguments.get("deviceType", "")
            provisioned = arguments.get("provisioned", "")
            project = arguments.get("project", "")
            q = arguments.get("q", "")
            query = f"?page={page}&limit={limit}&deviceType={deviceType}&provisioned={provisioned}&project={project}&q={q}"
            print(query)
            return getDevices(query)
        case "getDeviceData":
            deviceId = arguments.get("deviceId", "")
            startDate = arguments.get("startDate", "")
            endDate = arguments.get("endDate", "")
            query = f"?start={startDate}&end={endDate}"
            print(query)
            return getDeviceData(deviceId, query)
        case "getDeviceEventData":
            deviceId = arguments.get("deviceId", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
            print(query)
            return getDeviceData(deviceId, query)
        case "getDeviceLocationData":
            deviceId = arguments.get("deviceId", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
            print(query)
            return getDeviceData(deviceId, query)
        case "getDeviceAccelerationData":
            deviceId = arguments.get("deviceId", "")
            t = arguments.get("timePeriod", "")
            query = f"?t={t}"
            print(query)
            return getDeviceData(deviceId, query)
        case "getProjects":
            return getProjects()
        case "getProject":
            projectName = arguments.get("projectName", "")
            return getProject(projectName)
        case "getDevicesInProject":
            projectName = arguments.get("projectName", "")
            return getDevicesInProject(projectName)


client = OpenAI(api_key='sk-proj-VIa0xmeWs7LG6lyHmleST3BlbkFJLyhuWf28HAXT88QhN25M', organization='org-qRa4NGJi0VworFbpu3ymwscd')

assistant = client.beta.assistants.create(
    name="TNT Assistant",
    instructions="You are a helpful assistant that retrieve information for the user. First, you will identify what information the user wants to get, parse user queries and extract relevant parameters, and match it to corresponding function name and description. Then, call the function with the corresponding arguments. You can ask the user to provide any missing parameters required for the function call. \n If you are unsure about user's request, ask for more information. If you are unable to help, gracefully rejecting their request.",
    model="gpt-3.5-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "getAssetTypes",
                "description": "Get information of asset types",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getAssets",
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
                            "description": "The ID of the project which user filters out assets by. User will only search with the name of the project, so look through all the projects and find its ID",
                        },
                        "q": {
                            "type": "string",
                            "description": "The ID of the asset or ID of the device user search by",
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
                "name": "getAsset",
                "description": "Get information of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assetName": {
                            "type": "string",
                            "description": "The name of the asset",
                        },
                    },
                    "required": ["assetName"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getAssetSensorData",
                "description": "Get sensor data of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assetName": {
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
                    "required": ["assetName"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getAssetsWithLocation",
                "description": "Get information of assets with their locations",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getDevices",
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
                            "description": "The number of rows of assets displaying to the user per page",
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
                "name": "getDeviceData",
                "description": "Get general data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceId": {
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
                    "required": ["deviceId"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getDeviceEventData",
                "description": "Get event data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceId": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["deviceId"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getDeviceLocationData",
                "description": "Get location data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceId": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["deviceId"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getDeviceAccelerationData",
                "description": "Get acceleration data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceId": {
                            "type": "string",
                            "description": "The ID of the device",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
                        },
                    },
                    "required": ["deviceId"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getProjects",
                "description": "Get information of projects",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getProject",
                "description": "Get information of a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "The name of the project",
                        }
                    },
                    "required": ["projectName"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "getDevicesInProject",
                "description": "Get information of devices in a project",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "The name of the project",
                        }
                    },
                    "required": ["projectName"],
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
        )
    ).launch(share=True)
