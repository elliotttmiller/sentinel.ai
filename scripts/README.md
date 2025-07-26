# Sentinel Service Manager

A comprehensive Python script to manage all Sentinel services on Windows.

## Features

- **Start/Stop Services**: Manage backend server, ngrok tunnel, and agent engine
- **Interactive Menu**: Easy-to-use menu system
- **Command Line Interface**: Quick commands for automation
- **Configuration Management**: Save and load service settings
- **Background Mode**: Start services and exit, leaving them running
- **Status Monitoring**: Check which services are running

## Installation

1. Install dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. Make sure ngrok is installed and authenticated

## Usage

### Interactive Mode (Default)
```bash
python scripts/manage_services.py
```

### Command Line Mode
```bash
# Check service status
python scripts/manage_services.py --status

# Start all services
python scripts/manage_services.py --start-all

# Stop all services
python scripts/manage_services.py --stop-all

# Start specific services
python scripts/manage_services.py --start-backend
python scripts/manage_services.py --start-ngrok
python scripts/manage_services.py --start-engine

# Configure services
python scripts/manage_services.py --config
```

## Configuration

The script creates a `service_config.json` file in the `scripts/` directory with default settings:

```json
{
  "backend": {
    "port": 8080,
    "host": "0.0.0.0",
    "reload": true
  },
  "ngrok": {
    "port": 8080,
    "subdomain": null
  },
  "engine": {
    "port": 8001,
    "host": "0.0.0.0"
  }
}
```

You can modify these settings through the interactive menu or by editing the JSON file directly.

## Services Managed

1. **Backend Server** (uvicorn)
   - Runs the FastAPI backend server
   - Configurable port and auto-reload

2. **ngrok Tunnel**
   - Creates public tunnel to your local services
   - Configurable port and subdomain

3. **Agent Engine**
   - Runs the local agent execution engine
   - Handles AI agent workflows

## Tips

- Use option 11 (Start Services in Background) to start all services and exit the script
- Services will continue running in separate console windows
- Use `--status` to check if services are still running
- Use `--stop-all` to stop all services when done

## Troubleshooting

- **Service won't start**: Check if the port is already in use
- **ngrok errors**: Make sure ngrok is authenticated (`ngrok config add-authtoken`)
- **Backend errors**: Check that you're in the correct directory and dependencies are installed
- **Engine errors**: Verify the engine directory structure and dependencies 