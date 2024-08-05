# Importing necessary configurations and OpenAI library
from config import api_key, organization_id
from openai import OpenAI
from datetime import date

today = date.today()
print(today)

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
    instructions=f"""
        You are a helpful assistant that retrieves information for the user.

        You will identify what information the user wants by parsing user queries and extracting relevant parameters, and call the function with the corresponding arguments to get information. You can ask the user to provide any missing parameters required for the function call.

        If you are unsure about the user's request, ask to clarify. If you are unable to help, gracefully reject their request.

        Rules when parsing user queries:
        - Today is {today}. If the user requests information related to the current date, interpret key phrases such as "Past day," "Yesterday," "Last week," and "Previous month" in the context of today's date.
        - When the user queries for data within a specific date range, both start and end dates need to be intepreted, never have only one of the dates, assume for the other bound if only one date is given by the user. E.g. User inputs: "Show me data since yesterday.", then start date will be yesterday and end date will be assumed to be today inclusive.

        Rules when responding to the user:
        - If the function outputs nothing (None or null), respond to the user with a message indicating that no data was found.
        - Always respond to the user in markdown format, create tables for tabular data.
        - Always convert Unix Epoch timestamps and ISO 8601 format timestamps to human-readable date and time (24-hour time notation), then offset the hour by -7 to adjust the timezone from UTC to PDT.
        - If the user asks for a report, indicate to the user to use the download button if the report is generated and ready to be downloaded.
        """,
    model="gpt-4o-mini",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_alerts",
                "description": "Return alerts/excursions based on user-defined parameters. Excursions are alerts that are triggered when a sensor value exceeds a certain threshold (E.g. Temperature, Trip Duration, Lifetime Temperature). The response includes a pagination support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The page number of the assets to return.",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of assets per page, default to 50.",
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
                            "description": "The start date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) from which to filter assets. E.g. User inputs: 'Show me alerts from the past week.', then set startDate to one week before today.",
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) until which to filter assets. E.g. User inputs: 'Show me alerts until yesterday.', then set endDate to yesterday.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset_sensor_data",
                "description": "Return sensor data of an asset given the asset name. E.g. timestamps, temperature (C), pressure (hPa), and acceleration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Get me sensor data for my asset X.', then asset_name = 'X'.",
                        }
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_assets",
                "description": "Returns assets based on user-defined parameters. The response includes a pagination support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The page number of the assets to return.",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of assets per page, default to 50.",
                        },
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
                            "description": "The start date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) from which to filter assets. E.g. User inputs: 'Show me assets from the past week.', then set startDate to one week before today.",
                        },
                        "endDate": {
                            "type": "string",
                            "description": "The end date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) until which to filter assets. E.g. User inputs: 'Show me assets until yesterday.', then set endDate to yesterday.",
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
                            "description": "The start date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) from which to retrieve device data. E.g. User inputs: 'Get me data from device X from yesterday.', then set start to yesterday.",
                        },
                        "end": {
                            "type": "string",
                            "description": "The end date and time in ISO 8601 format (E.g. 2024-06-22T18:15:48.030Z) until which to retrieve device data. E.g. User inputs: 'Get me data from device X until today.', then set end to today.",
                        },
                    },
                    "required": ["device_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_device_events",
                "description": "Return events of a device based on user-defined parameters. Events such as movement, open, close, short, medium, and shock.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the device. E.g. User inputs: 'Is there any events happend on device X during the trip?', then device_id = 'X'.",
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
                "description": "Return devices based on user-defined parameters. The response includes a pagination support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "The page number of the assets to return.",
                        },
                        "limit": {
                            "type": "string",
                            "description": "The number of assets per page, default to 50.",
                        },
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
                "name": "get_projects",
                "description": "Return projects.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_asset_pdf_report",
                "description": "Generate a PDF report for a specific asset identified by its name. E.g. User inputs: 'Generate a report for asset X.', then asset_name = 'X'; User inputs: 'Generate a report for X.', then asset_name = 'X'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset for which the PDF report is requested. E.g. User inputs: 'Generate a report for asset X.', then asset_name = 'X'.",
                        },
                        "orgId": {
                            "type": "string",
                            "description": "ID of the organization the Asset belongs to.",
                        },
                        "ts": {
                            "type": "string",
                            "description": "This timestamp, measured in milliseconds, determines the closest report generated to it that will be returned.",
                        },
                    },
                    "required": ["asset_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_visuals",
                "description": "Provide a link to view an asset's temperature, pressure, and acceleration graphs, and location on a map.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_name": {
                            "type": "string",
                            "description": "The name of the asset. E.g. User inputs: 'Show me temperature graph for asset X.', then asset_name = 'X'. User inputs: 'Show me the location of asset X.', then asset_name = 'X'.",
                        }
                    },
                    "required": ["asset_name"],
                },
            },
        },
    ],
)
