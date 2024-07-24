# Tag-N-Trac AI Assistant

## Overview
This project aims to integrate an AI assistant into a device tracking system to enhance user experience by allowing natural language queries. The assistant will help users search for devices, track shipments, view temperature graphs, look for excursions, and download PDF reports.

## Features
1. Natural Language Search: Users can search for devices and shipments using natural language instead of traditional filter boxes.
2. Lifecycle Tracking: Track the lifecycle of an asset from provisioning to deprovisioning, including all significant events with timestamps.
3. Excursion Detection: Monitor and report any excursions during the lifecycle of the assets.
4. Temperature Graphs: View detailed temperature graphs of the assets.
5. PDF Reports: Generate and download comprehensive PDF reports of the asset's lifecycle and excursions.

## Technology Stacks 
- Frontend: Gradio
- Backend: Python
- AI Model: OpenAI's GPT-4

## Installation
1. Clone the repository:
```
git clone https://github.com/yourusername/ai-assistant-device-tracking.git
cd ai-assistant-device-tracking
```
2. Set up a virtual environment and activate it:
```
python3 -m venv venv
source venv/bin/activate
```
3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage
1. Run the AI assistant application:
```
python app.py
```
2. Open your web browser and go to the local server address (e.g., `http://localhost:7860`) to interact with the assistant.

## Configuration
Ensure that your API keys and other sensitive information are stored securely. You can use environment variables or a `.env` file to manage these configurations.

## Contribution
We welcome contributions to enhance this project. If you wish to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch `git checkout -b new-branch`.
3. Make your changes and commit them `git commit -am 'add changes _ '`.
4. Push to the branch `git push origin new-branch`.
5. Create a new Pull Request.

## License


## Contact
For any inquiries or issues, please reach out to Tag-N-Trac or justin.yang@tagntrac.com or create an issue in the GitHub repository.
