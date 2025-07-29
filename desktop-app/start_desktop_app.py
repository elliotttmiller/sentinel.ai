import os
import subprocess
import sys
import time
import traceback
from loguru import logger

APP_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(APP_DIR, "requirements.txt")
ENV_FILE = os.path.join(APP_DIR, ".env")
MAIN_FILE = os.path.join(APP_DIR, "main.py")
LOG_FILE = os.path.join(APP_DIR, "startup_debug.log")

# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time}</green> <level>{level: <8}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
logger.add(LOG_FILE, level="DEBUG", rotation="1 MB", retention="10 days")


def log_exception(e, context=""):
    logger.error(f"{context} Exception: {e}")
    logger.debug(traceback.format_exc())
    print(f"    ✗ {context} Exception: {e}")
    print(f"    See {LOG_FILE} for full stack trace.")


def check_requirements():
    print("[1/5] Checking Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS])
        logger.info("All dependencies installed.")
        print("    ✓ All dependencies installed.")
    except subprocess.CalledProcessError as e:
        log_exception(e, "Dependency installation failed.")
        sys.exit(1)


def check_env():
    print("[2/5] Checking .env file...")
    if not os.path.exists(ENV_FILE):
        logger.error(f".env file not found at {ENV_FILE}")
        print(f"    ✗ .env file not found at {ENV_FILE}")
        sys.exit(1)
    logger.info(".env file found.")
    print("    ✓ .env file found.")


def check_db_connection():
    print("[3/5] Testing database connection...")
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_FILE)
        import sqlalchemy
        from sqlalchemy import create_engine

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise Exception("DATABASE_URL not set in .env file.")
        engine = create_engine(db_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        logger.info("Database connection successful.")
        print("    ✓ Database connection successful.")
    except Exception as e:
        log_exception(e, "Database connection failed.")
        sys.exit(1)


def run_tests():
    print("[4/5] Running core import and logic tests...")
    try:
        import agent_logic
        import db

        # Test agent logic with a dummy prompt (does not call LLM)
        if hasattr(agent_logic, "run_simple_agent_task"):
            try:
                agent_logic.run_simple_agent_task("Test prompt for startup diagnostics.")
                logger.info("Agent logic test passed.")
            except Exception as agent_e:
                logger.warning(f"Agent logic test failed: {agent_e}")
        logger.info("Core modules import successfully.")
        print("    ✓ Core modules import successfully.")
    except Exception as e:
        log_exception(e, "Import or logic test failed.")
        sys.exit(1)


def start_server():
    print("[5/5] Starting Sentinel Desktop App server...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"], cwd=APP_DIR
        )
        logger.info("Server started. Open http://localhost:8001 in your browser.")
        print("    ✓ Server started. Open http://localhost:8001 in your browser.")
        print("    (Press CTRL+C to stop the server)")
        proc.wait()
    except KeyboardInterrupt:
        print("\n    Server stopped by user.")
        logger.info("Server stopped by user.")
    except Exception as e:
        log_exception(e, "Failed to start server.")
        sys.exit(1)


def main():
    print("\n=== Sentinel Desktop App Startup ===\n")
    logger.info("=== Sentinel Desktop App Startup ===")
    try:
        check_requirements()
        check_env()
        check_db_connection()
        run_tests()
        start_server()
    except Exception as e:
        log_exception(e, "Fatal error during startup.")
        sys.exit(1)


if __name__ == "__main__":
    main()
