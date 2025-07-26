import os

# Auto-create logs and workspace directories
logs_dir = os.getenv("LOGS_DIR", "./logs")
workspace_dir = os.getenv("WORKSPACE_DIR", "./workspace")
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(workspace_dir, exist_ok=True)

# Validate required environment variables
required_vars = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "VECTOR_DB_TYPE",
    "VECTOR_DB_PATH"
]
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f"WARNING: Missing required environment variables: {', '.join(missing)}")
else:
    print("All required environment variables are set.") 