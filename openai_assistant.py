# Importing necessary configurations and OpenAI library
from config import api_key, organization_id
from openai import OpenAI

# Initializing OpenAI client with provided API key and organization ID
client = OpenAI(api_key=api_key, organization=organization_id)

# Script to delete past assistants
my_assistants = client.beta.assistants.list()
# Loop through each assistant and delete it
for assistant in my_assistants.data:
    # print("Deleting assistant: " + assistant.id)
    client.beta.assistants.delete(assistant.id)

# Create a new assistant with specified name, instructions, model, and tools
assistant = client.beta.assistants.create(
    name="TNT AI Assistant",
    instructions="""
        You are a helpful assistant that retrieves information for the user.

        You will identify what information the user wants by parsing user queries and extracting relevant parameters, and call the function with the corresponding arguments to get information. You can ask the user to provide any missing parameters required for the function call.

        If you are unsure about the user's request, ask to clarify. If you are unable to help, gracefully reject their request.

        Some rules to follow:
        - If the function outputs nothing (None or null), respond to the user with a message indicating that no data was found.
        - Always respond to the user in markdown format, create tables for tabular data.
        - If the user asks for a report, indicate to the user to use the download button if the report is generated and ready to be downloaded.
        - Always convert unix timestamps to human-readable time before displaying time information the user.
        - Display up to 5 most recent results, indicate to the user if there are more results not displayed.
        """,
    model="gpt-3.5-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_alerts",
                "description": "Return alerts based on user-defined parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parameter": {
                            "type": "string", 
                            "description": "The parameter to filter alerts by.",
                        },
                        "condition": {
                            "type": "string", 
                            "description": "The condition to filter alerts by.",
                        },
                        "project": {
                            "type": "string",
                            "description": "The name of the project which user filters out assets by. E.g. User inputs: 'I want to see alerts from project X.', then project = 'X'.",
                        },
                        "q": {
                            "type": "string",
                            "description": "The name of the asset or ID of the device user search by, a way to search for alerts related to a specific asset or device. E.g. User inputs: 'I want to see alerts on asset X.', then q = 'X'; User inputs: 'I want to see alerts on device X.', then q = 'X'.",
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
                "description": "Return information of an asset given the asset name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Tell me about asset X.', then asset_name = 'X'.",
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
                "description": "Return alerts of an asset given the asset name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Show me alerts from my asset X.', then asset_name = 'X'.",
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
                "description": "Return sensor data of an asset given the asset name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Get me sensor data for my asset X.', then asset_name = 'X'.",
                        },
                        "timePeriod": {
                            "type": "string",
                            "description": "The period of time in minutes user wants the data from. E.g. User inputs: 'Get me sensor data for my asset X in the past day.', then timePeriod = 1440, because 1 day is 1440 minutes; User inputs: 'Get me sensor data for my asset X in the past 2 days.', then timePeriod = 2880, because 2 days is 2880 minutes.",
                        },
                        "binInterval": {
                            "type": "string",
                            "description": "The time interval in minutes that user wants the data in. E.g. User inputs: 'Get me sensor data for my asset X in the past day in every 15 minutes interval.', then binInterval = 15.",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_assets",
                "description": "Returns assets based on user-defined parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceType": {
                            "type": "string",
                            "description": "The type of device the user filters for: deviceType = BLE_TAG for bluetooth, CATM1_TAG for cellular, NFC_TAG for NFC. E.g. User inputs: 'Show me all bluetooth devices.', then deviceType = BLE_TAG.",
                        },
                        "assetType": {
                            "type": "string",
                            "description": "The type of asset the user filters for: assetType = UNIT for unit, BOX for box, PALLET for pallet, CONTAINER for container. E.g. User inputs: 'Show me all assets in pallets.', then assetType = PALLET.",
                        },
                        "project": {
                            "type": "string",
                            "description": "The name of the project which user filters out assets by. E.g. User inputs: 'Show me all assets in project X.', then project = 'X'.",
                        },
                        "q": {
                            "type": "string",
                            "description": "The name of the asset or ID of the device user search by. E.g. User inputs: 'Show me asset X.', then q = 'X'; User inputs: 'Show me assets with device X.', then q = 'X'.",
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
                "name": "get_assets_with_location",
                "description": "Returns assets along with their location data.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_data",
                "description": "Return device data based on user-defined parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device. E.g. User inputs: 'Get me data from device X.', then device_id = 'X'.",
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
                "description": "Return event data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device. E.g. User inputs: 'Get me event data from device X.', then device_id = 'X'.",
                        },
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. E.g. User inputs: 'Get me event data from device X in the past day.', then t = 1440, because 1 day is 1440 minutes; User inputs: 'Get me event data from device X in the past 2 days.', then t = 2880, because 2 days is 2880 minutes.",
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
                "description": "Return location data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device. E.g. User inputs: 'Get me location data from device X.', then device_id = 'X'.",
                        },
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. E.g. User inputs: 'Get me location data from device X in the past day.', then t = 1440, because 1 day is 1440 minutes; User inputs: 'Get me location data from device X in the past 2 days.', then t = 2880, because 2 days is 2880 minutes.",
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
                "description": "Return acceleration data of a device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device. E.g. User inputs: 'Get me acceleration data from device X.', then device_id = 'X'.",
                        },
                        "t": {
                            "type": "string",
                            "description": "time period, the period of time in minutes user wants the data from. E.g. User inputs: 'Get me acceleration data from device X in the past day.', then t = 1440, because 1 day is 1440 minutes; User inputs: 'Get me acceleration data from device X in the past 2 days.', then t = 2880, because 2 days is 2880 minutes.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_devices",
                "description": "Return devices based on user-defined parameters.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "deviceType": {
                            "type": "string",
                            "description": "The type of device the user filters for: deviceType = BLE_TAG for bluetooth, CATM1_TAG for cellular, NFC_TAG for NFC. E.g. User inputs: 'Show me all bluetooth devices.', then deviceType = BLE_TAG.",
                        },
                        "provisioned": {
                            "type": "string",
                            "description": "The status of the device: deployed or in stock. Set provisioned to true if deployed, false if in stock. E.g. User inputs: 'Show me all deployed devices.', then provisioned = true.",
                        },
                        "project": {
                            "type": "string",
                            "description": "The ID of the project which user filters out assets by. E.g. User inputs: 'Show me all devices in project X.', then project = 'X'.",
                        },
                        "q": {
                            "type": "string",
                            "description": "The name of the asset or ID of the device user search by. E.g. User inputs: 'Show me device X.', then q = 'X'; User inputs: 'Show me devices in asset X.', then q = 'X'.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_devices_in_project",
                "description": "Return devices in a project given the project name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project. E.g. User inputs: 'Show me devices in project X.', then project_name = 'X'.",
                        }
                    },
                    "required": ["project_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_project",
                "description": "Return information of a project given the project name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "The name of the project. E.g. User inputs: 'Tell me about project X.', then project_name = 'X'.",
                        }
                    },
                    "required": ["project_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_projects",
                "description": "Return projects based on user-defined parameters.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_report_pdf",
                "description": "Generate a report of an asset in PDF format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Generate a report for asset X.', then asset_name = 'X'.",
                        },
                        "start": {
                            "type": "string",
                            "description": "The start date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) from which to retrieve device data",
                        },
                        "end": {
                            "type": "string",
                            "description": "The end date and time (in ISO 8601 format, i.e. YYYY-MM-DD for date, delimiter that separates the date from the time, hh:mm:ss.sss for time, and time zone) until which to retrieve device data",
                        },
                        "dataType": {
                            "type": "string",
                            "description": "The type of data user wants to retrieve.",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_excursions",
                "description": "Provide a link to view the excursion of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Show me excursion for asset X.', then asset_name = 'X'.",
                        }
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_temp_graph",
                "description": "Provide a link to view the temperature graph of an asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Show me temperature graph for asset X.', then asset_name = 'X'.",
                        }
                    },
                    "required": ["asset_name"],
                },
            },
        },
    ],
)
