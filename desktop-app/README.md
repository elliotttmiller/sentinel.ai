# Sentinel Desktop App (Local-Only)

This directory contains a fully self-contained, local-only version of the Sentinel agent command center. It is designed for personal use on your desktop, with no cloud, tunnel, or mobile app dependencies required.

## Features
- Simple web UI for entering prompts and viewing agent results
- FastAPI backend running locally
- Direct integration with CrewAI and LangChain for agent logic
- No user accounts, no multi-user logic
- Can be extended with desktop automation, local file I/O, and more

## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `uvicorn main:app --reload --port 8001`
3. Open your browser to [http://localhost:8001](http://localhost:8001)

## Notes
- This app is for local, personal use only. It does not expose any public endpoints.
- The rest of the Sentinel system (mobile app, backend, cloud) remains available and unchanged.
- If you want to add desktop automation or other features, see the TODOs in this directory. 