#!/usr/bin/env python3
"""
Automated Debugger Service
Continuously monitors Sentry for errors and automatically triggers Fix-AI to resolve them
"""

import asyncio
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

# Import Sentry API client
try:
    from .sentry_api_client import fetch_recent_sentry_errors

    SENTRY_API_AVAILABLE = True
except ImportError:
    SENTRY_API_AVAILABLE = False
    logger.warning("Sentry API not available. Automated debugging will be limited.")


class AutomatedDebugger:
    """Automated debugging service that monitors Sentry and triggers Fix-AI"""

    def __init__(self, check_interval: int = 300):  # Check every 5 minutes
        self.check_interval = check_interval
        self.last_check = None
        self.processed_errors = set()
        self.error_history = []
        self.fix_ai_path = Path(__file__).parent.parent.parent / "Fix-AI.py"
        self.is_running = False

        logger.info("Automated Debugger initialized")

    async def start_monitoring(self):
        """Start the automated debugging monitoring loop"""
        self.is_running = True
        logger.info("Starting automated debugging monitoring...")

        while self.is_running:
            try:
                await self.check_for_new_errors()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def check_for_new_errors(self):
        """Check for new errors in Sentry and trigger Fix-AI if needed"""
        if not SENTRY_API_AVAILABLE:
            logger.warning("Sentry API not available. Skipping error check.")
            return

        try:
            logger.info("Checking for new Sentry errors...")

            # Fetch recent errors from Sentry
            recent_errors = fetch_recent_sentry_errors(hours=1)  # Last hour

            if not recent_errors:
                logger.info("No recent errors found in Sentry")
                return

            # Filter for new errors we haven't processed
            new_errors = []
            for error in recent_errors:
                error_id = error.get("issue_id", "unknown")
                if error_id not in self.processed_errors:
                    new_errors.append(error)
                    self.processed_errors.add(error_id)

            if new_errors:
                logger.info(f"Found {len(new_errors)} new errors. Triggering Fix-AI...")
                await self.trigger_fix_ai(new_errors)
            else:
                logger.info("No new errors to process")

        except Exception as e:
            logger.error(f"Error checking Sentry: {e}")

    async def trigger_fix_ai(self, errors: List[Dict[str, Any]]):
        """Trigger Fix-AI to resolve the detected errors"""
        try:
            logger.info(f"Triggering Fix-AI for {len(errors)} errors")

            # Log the errors for Fix-AI
            self._log_errors_for_fix_ai(errors)

            # Run Fix-AI
            await self._run_fix_ai()

            # Update error history
            self.error_history.extend(errors)

            # Keep only last 100 errors in history
            if len(self.error_history) > 100:
                self.error_history = self.error_history[-100:]

        except Exception as e:
            logger.error(f"Error triggering Fix-AI: {e}")

    def _log_errors_for_fix_ai(self, errors: List[Dict[str, Any]]):
        """Log errors in a format that Fix-AI can process"""
        try:
            logs_dir = Path(__file__).parent.parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)

            error_log_file = logs_dir / "sentry_errors.json"

            # Load existing errors
            existing_errors = []
            if error_log_file.exists():
                with open(error_log_file, "r") as f:
                    existing_errors = json.load(f)

            # Add new errors
            for error in errors:
                error["detected_at"] = datetime.now().isoformat()
                existing_errors.append(error)

            # Save updated errors
            with open(error_log_file, "w") as f:
                json.dump(existing_errors, f, indent=2)

            logger.info(f"Logged {len(errors)} errors for Fix-AI processing")

        except Exception as e:
            logger.error(f"Error logging errors for Fix-AI: {e}")

    async def _run_fix_ai(self):
        """Run Fix-AI to resolve the detected errors"""
        try:
            if not self.fix_ai_path.exists():
                logger.error("Fix-AI.py not found")
                return

            # Import and run Fix-AI dynamically
            spec = importlib.util.spec_from_file_location("Fix_AI", self.fix_ai_path)
            Fix_AI = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(Fix_AI)

            # Create healer instance and run
            healer = Fix_AI.CodebaseHealer(self.fix_ai_path.parent)
            healer.run()

            logger.success("Fix-AI completed successfully")

        except Exception as e:
            logger.error(f"Error running Fix-AI: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the automated debugger"""
        return {
            "is_running": self.is_running,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "processed_errors_count": len(self.processed_errors),
            "error_history_count": len(self.error_history),
            "check_interval_seconds": self.check_interval,
            "sentry_api_available": SENTRY_API_AVAILABLE,
        }

    def stop_monitoring(self):
        """Stop the automated debugging monitoring"""
        self.is_running = False
        logger.info("Automated debugging monitoring stopped")


# Global automated debugger instance
automated_debugger = None


def get_automated_debugger() -> AutomatedDebugger:
    """Get or create the global automated debugger instance"""
    global automated_debugger
    if automated_debugger is None:
        automated_debugger = AutomatedDebugger()
    return automated_debugger


async def start_automated_debugging():
    """Start the automated debugging service"""
    debugger = get_automated_debugger()
    await debugger.start_monitoring()


def stop_automated_debugging():
    """Stop the automated debugging service"""
    debugger = get_automated_debugger()
    debugger.stop_monitoring()


# Test function
async def test_automated_debugger():
    """Test the automated debugger functionality"""
    logger.info("Testing automated debugger...")

    debugger = get_automated_debugger()

    # Test error checking
    await debugger.check_for_new_errors()

    # Get status
    status = debugger.get_status()
    logger.info(f"Debugger status: {json.dumps(status, indent=2)}")

    logger.success("Automated debugger test completed")


if __name__ == "__main__":
    asyncio.run(test_automated_debugger())
