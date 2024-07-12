from openai import OpenAI
from config import api_key, organization_id

client = OpenAI(api_key=api_key, organization=organization_id)

# temp script for deleting past assistants
# my_assistants = client.beta.assistants.list()
# for assistant in my_assistants.data:
#     print("Deleting assistant: " + assistant.id)
#     client.beta.assistants.delete(assistant.id)

assistant = client.beta.assistants.create(
    name="TNT AI Assistant",
    instructions="""
        You are a helpful assistant that retrieves information for the user.

        You will identify what information the user wants by parsing user queries and extracting relevant parameters, and call the function with the corresponding arguments to get information. You can ask the user to provide any missing parameters required for the function call.

        If you are unsure about the user's request, ask to clarify. If you are unable to help, gracefully reject their request.

        Some rules to follow:
        - Our server stores timestamps in unix form, convert between unix and human-readable to interact with the user. Always convert unix timestamps received from function calls to human-readable date and time format to display to the user.
        - Show up to 8 results, indicate to the user if there are more than 8.
        - The user is in PDT time zone.
        """,
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
                        "parameter": {"type": "string", "description": ""},
                        "condition": {"type": "string", "description": ""},
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
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to filter assets",
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to filter assets",
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
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to filter assets",
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to filter assets",
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
                        "start": {
                            "type": "string",
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to retrieve device data",
                        },
                        "end": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to retrieve device data",
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
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
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
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
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
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. e.g. time period is 1440 if user ask for data within 1 day, 2880 for 2 days etc.",
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
