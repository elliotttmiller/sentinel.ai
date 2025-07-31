#!/usr/bin/env python3
"""
Sentry API Client for Automated Debugging and Fixing
Fetches real error data from Sentry for integration with Fix-AI
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class SentryAPIClient:
    """Client for interacting with Sentry API to fetch error data"""
    
    def __init__(self, org_slug: Optional[str] = None, project_id: Optional[str] = None):
        self.auth_token = os.getenv("SENTRY_AUTH_TOKEN")
        self.org_slug = org_slug or os.getenv("SENTRY_ORG_SLUG")
        self.project_id = project_id or os.getenv("SENTRY_PROJECT_ID")
        self.base_url = "https://sentry.io/api/0"
        
        if not self.auth_token:
            logger.warning("SENTRY_AUTH_TOKEN not found. API calls will be limited.")
    
    def get_recent_issues(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch recent issues from Sentry"""
        if not self.auth_token or not self.org_slug or not self.project_id:
            logger.warning("Sentry API credentials not configured. Using simulated data.")
            return self._get_simulated_issues()
        
        try:
            # Use project ID in the URL
            url = f"{self.base_url}/projects/{self.org_slug}/{self.project_id}/issues/"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            # Get issues from the last N hours
            since = datetime.now() - timedelta(hours=hours)
            params = {
                "query": f"firstSeen:>={since.isoformat()}",
                "statsPeriod": f"{hours}h"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            return self._process_issues(issues)
            
        except Exception as e:
            logger.error(f"Failed to fetch Sentry issues: {e}")
            return self._get_simulated_issues()
    
    def get_issue_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific issue"""
        if not self.auth_token or not self.org_slug or not self.project_id:
            return None
        
        try:
            url = f"{self.base_url}/issues/{issue_id}/"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch issue details: {e}")
            return None
    
    def get_issue_events(self, issue_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events for a specific issue"""
        if not self.auth_token or not self.org_slug or not self.project_id:
            return []
        
        try:
            url = f"{self.base_url}/issues/{issue_id}/events/"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            params = {"limit": limit}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch issue events: {e}")
            return []
    
    def _process_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw Sentry issues into a format suitable for Fix-AI"""
        processed_issues = []
        
        for issue in issues:
            try:
                # Extract error information
                error_info = self._extract_error_info(issue)
                if error_info:
                    processed_issues.append(error_info)
            except Exception as e:
                logger.error(f"Failed to process issue {issue.get('id')}: {e}")
        
        return processed_issues
    
    def _extract_error_info(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract relevant error information from a Sentry issue"""
        try:
            # Get the most recent event for stack trace
            events = self.get_issue_events(issue.get('id', ''), limit=1)
            
            file_path = "unknown"
            line_number = 0
            
            if events:
                event = events[0]
                # Extract file path and line number from stack trace
                stack_trace = self._extract_stack_trace(event)
                if stack_trace:
                    file_path = stack_trace.get('file_path', 'unknown')
                    line_number = stack_trace.get('line_number', 0)
            
            return {
                "error_type": issue.get('type', 'Unknown'),
                "message": issue.get('title', 'Unknown error'),
                "file_path": file_path,
                "line": line_number,
                "frequency": issue.get('count', 1),
                "last_seen": issue.get('lastSeen', datetime.now().isoformat()),
                "suggested_fix": self._generate_suggested_fix(issue),
                "issue_id": issue.get('id'),
                "severity": issue.get('level', 'error')
            }
            
        except Exception as e:
            logger.error(f"Failed to extract error info: {e}")
            return None
    
    def _extract_stack_trace(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract file path and line number from event stack trace"""
        try:
            # Look for stack trace in the event
            if 'entries' in event:
                for entry in event['entries']:
                    if entry.get('type') == 'exception':
                        for exception in entry.get('data', {}).get('values', []):
                            if 'stacktrace' in exception:
                                frames = exception['stacktrace'].get('frames', [])
                                if frames:
                                    # Get the most recent frame (last in the list)
                                    frame = frames[-1]
                                    return {
                                        "file_path": frame.get('filename', 'unknown'),
                                        "line_number": frame.get('lineno', 0)
                                    }
        except Exception as e:
            logger.error(f"Failed to extract stack trace: {e}")
        
        return None
    
    def _generate_suggested_fix(self, issue: Dict[str, Any]) -> str:
        """Generate a suggested fix based on error type and message"""
        error_type = issue.get('type', '').lower()
        message = issue.get('title', '').lower()
        
        # Common error patterns and suggested fixes
        if 'attributeerror' in error_type:
            if 'none' in message and 'get' in message:
                return "Check if object is None before calling .get() method"
            elif 'has no attribute' in message:
                return "Verify the object type and ensure the attribute exists"
        
        elif 'typeerror' in error_type:
            if 'none' in message:
                return "Add null check before operation"
            elif 'argument' in message:
                return "Check argument types and ensure they match expected signature"
        
        elif 'syntaxerror' in error_type:
            return "Fix syntax error in the specified file and line"
        
        elif 'importerror' in error_type:
            return "Check if the module is installed and import path is correct"
        
        elif 'keyerror' in error_type:
            return "Check if the key exists in the dictionary before accessing"
        
        return "Review the error context and apply appropriate fix"
    
    def _get_simulated_issues(self) -> List[Dict[str, Any]]:
        """Return simulated issues for testing when API is not available"""
        return [
            {
                "error_type": "AttributeError",
                "message": "object has no attribute 'get'",
                "file_path": "src/core/cognitive_forge_engine.py",
                "line": 245,
                "frequency": 3,
                "last_seen": datetime.now().isoformat(),
                "suggested_fix": "Check if object is None before calling .get() method",
                "issue_id": "simulated-1",
                "severity": "error"
            },
            {
                "error_type": "TypeError",
                "message": "can't multiply sequence by non-int of type 'NoneType'",
                "file_path": "src/utils/weave_observability.py",
                "line": 156,
                "frequency": 2,
                "last_seen": datetime.now().isoformat(),
                "suggested_fix": "Add null check before multiplication operation",
                "issue_id": "simulated-2",
                "severity": "error"
            }
        ]


# Global Sentry API client instance
sentry_api_client = None


def get_sentry_api_client() -> SentryAPIClient:
    """Get or create the global Sentry API client"""
    global sentry_api_client
    if sentry_api_client is None:
        sentry_api_client = SentryAPIClient()
    return sentry_api_client


def fetch_recent_sentry_errors(hours: int = 24) -> List[Dict[str, Any]]:
    """Convenience function to fetch recent Sentry errors"""
    client = get_sentry_api_client()
    return client.get_recent_issues(hours) 