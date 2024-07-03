import time
import json
import gradio as gr
from openai import OpenAI

from api import getAssetTypes, getAssets, getAsset, getAssetSensorData, getAssetsWithLocation, getDeviceData, getProjects, getProject, getDevicesInProject


def get_function_output(function):
    arguments = json.loads(function.arguments)
    match function.name:
        case "getAssetTypes":
            return getAssetTypes()
        case "getAssets":
            return getAssets()
        case "getAsset":
            return getAsset(arguments["assetId"])
        case "getAssetSensorData":
            return getAssetSensorData(arguments["assetId"])
        case "getAssetsWithLocation":
            return getAssetsWithLocation()
        case "getDeviceData":
            return getDeviceData(arguments["deviceId"])
        case "getProjects":
            return getProjects()
        case "getProject":
            return getProject(arguments["projectId"])
        case "getDevicesInProject":
            return getDevicesInProject(arguments["projectId"])


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
                "description": "Get information of assets",
                "parameters": {"type": "object", "properties": {}, "required": []},
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
                        "assetId": {
                            "type": "string",
                            "description": "The ID of the asset",
                        }
                    },
                    "required": ["assetId"],
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
                        "assetId": {
                            "type": "string",
                            "description": "The ID of the asset",
                        }
                    },
                    "required": ["assetId"],
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
                "name": "getDeviceData",
                "description": "Get data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceId": {
                            "type": "string",
                            "description": "The ID of the device",
                        }
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
                        "projectId": {
                            "type": "string",
                            "description": "The ID of the project",
                        }
                    },
                    "required": ["projectId"],
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
                        "projectId": {
                            "type": "string",
                            "description": "The ID of the project",
                        }
                    },
                    "required": ["projectId"],
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

    tool_calls = run.required_action.submit_tool_outputs.tool_calls

    tool_outputs = []
    for tool_call in tool_calls:
        print(tool_call.function)
        function_output = json.dumps(get_function_output(tool_call.function))
        # print(function_output)
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
    
    messages = list(client.beta.threads.messages.list(thread_id=thread.id))
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
