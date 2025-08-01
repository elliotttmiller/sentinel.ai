#!/usr/bin/env python3
"""
Observability Configuration Guide
Setup real-time integrations for Weave, Sentry, and WandB
"""

import os
from typing import Dict, Any

# =============================================================================
# WEAVE OBSERVABILITY SETUP
# =============================================================================

def setup_weave_observability() -> Dict[str, Any]:
    """
    Setup Weave for real-time observability
    
    Requirements:
    1. Install Weave: pip install weave
    2. Set environment variables:
       - WEAVE_API_KEY (optional, for cloud features)
       - WEAVE_PROJECT_NAME (default: "cognitive-forge-v5")
    
    Usage:
    - Weave automatically tracks all mission executions
    - Provides real-time traces and performance metrics
    - Integrates with the Strategic Command Center dashboard
    """
    
    config = {
        "enabled": True,
        "project_name": os.getenv("WEAVE_PROJECT_NAME", "cognitive-forge-v5"),
        "api_key": os.getenv("WEAVE_API_KEY"),
        "features": [
            "Real-time mission tracing",
            "Agent performance metrics",
            "Execution time tracking",
            "Success rate monitoring",
            "Cost estimation",
            "Memory and CPU usage"
        ]
    }
    
    return config

# =============================================================================
# SENTRY OBSERVABILITY SETUP
# =============================================================================

def setup_sentry_observability() -> Dict[str, Any]:
    """
    Setup Sentry for error tracking and monitoring
    
    Requirements:
    1. Create a Sentry account at https://sentry.io
    2. Create a new project in Sentry
    3. Set environment variables:
       - SENTRY_AUTH_TOKEN (from Sentry API settings)
       - SENTRY_ORG_SLUG (your organization slug)
       - SENTRY_PROJECT_ID (your project ID)
       - SENTRY_DSN (for error reporting)
    
    Usage:
    - Automatically captures and reports errors
    - Provides real-time error rates and uptime
    - Shows active issues in the dashboard
    """
    
    config = {
        "enabled": bool(os.getenv("SENTRY_AUTH_TOKEN")),
        "auth_token": os.getenv("SENTRY_AUTH_TOKEN"),
        "org_slug": os.getenv("SENTRY_ORG_SLUG"),
        "project_id": os.getenv("SENTRY_PROJECT_ID"),
        "dsn": os.getenv("SENTRY_DSN"),
        "features": [
            "Real-time error tracking",
            "Error rate monitoring",
            "Uptime calculation",
            "Issue categorization",
            "Automatic error reporting"
        ]
    }
    
    return config

# =============================================================================
# WANDB OBSERVABILITY SETUP
# =============================================================================

def setup_wandb_observability() -> Dict[str, Any]:
    """
    Setup Weights & Biases for experiment tracking
    
    Requirements:
    1. Create a WandB account at https://wandb.ai
    2. Install WandB: pip install wandb
    3. Set environment variables:
       - WANDB_API_KEY (from WandB settings)
       - WANDB_PROJECT (default: "cognitive-forge-v5")
       - WANDB_ENTITY (your username or team name)
    
    Usage:
    - Tracks AI model performance and experiments
    - Monitors accuracy, loss, and other metrics
    - Provides experiment history and comparisons
    """
    
    config = {
        "enabled": bool(os.getenv("WANDB_API_KEY")),
        "api_key": os.getenv("WANDB_API_KEY"),
        "project": os.getenv("WANDB_PROJECT", "cognitive-forge-v5"),
        "entity": os.getenv("WANDB_ENTITY"),
        "features": [
            "Experiment tracking",
            "Model performance monitoring",
            "Accuracy and loss tracking",
            "Experiment comparison",
            "Real-time metrics"
        ]
    }
    
    return config

# =============================================================================
# ENVIRONMENT VARIABLES GUIDE
# =============================================================================

def get_environment_setup_guide() -> str:
    """
    Returns a comprehensive guide for setting up environment variables
    """
    
    guide = """
# =============================================================================
# OBSERVABILITY ENVIRONMENT SETUP GUIDE
# =============================================================================

## 1. WEAVE SETUP
# Add to your .env file:
WEAVE_PROJECT_NAME=cognitive-forge-v5
WEAVE_API_KEY=your_weave_api_key_here  # Optional

## 2. SENTRY SETUP
# Add to your .env file:
SENTRY_AUTH_TOKEN=your_sentry_auth_token_here
SENTRY_ORG_SLUG=your_organization_slug
SENTRY_PROJECT_ID=your_project_id
SENTRY_DSN=https://your_dsn_here@sentry.io/project_id

## 3. WANDB SETUP
# Add to your .env file:
WANDB_API_KEY=your_wandb_api_key_here
WANDB_PROJECT=cognitive-forge-v5
WANDB_ENTITY=your_username_or_team

## 4. HOW TO GET CREDENTIALS

### Weave:
1. Visit https://weave.ai
2. Create an account and project
3. Get API key from settings (optional)

### Sentry:
1. Visit https://sentry.io
2. Create account and organization
3. Create a new project
4. Go to Settings > API > Auth Tokens
5. Create a new token with project:read scope
6. Get Project ID from project settings
7. Get DSN from project settings

### WandB:
1. Visit https://wandb.ai
2. Create account
3. Go to Settings > API Keys
4. Create a new API key
5. Note your username/team name for entity

## 5. VERIFICATION

After setting up, restart your servers and check:
- Dashboard shows real-time data
- Observability Hub displays live metrics
- No "ERROR" status in any system
"""
    
    return guide

# =============================================================================
# INTEGRATION STATUS CHECKER
# =============================================================================

def check_integration_status() -> Dict[str, Any]:
    """
    Check the status of all observability integrations
    """
    
    status = {
        "weave": setup_weave_observability(),
        "sentry": setup_sentry_observability(),
        "wandb": setup_wandb_observability()
    }
    
    # Check if integrations are properly configured
    for system, config in status.items():
        if system == "weave":
            config["status"] = "READY" if config["enabled"] else "NOT_CONFIGURED"
        elif system == "sentry":
            config["status"] = "READY" if config["enabled"] else "NOT_CONFIGURED"
        elif system == "wandb":
            config["status"] = "READY" if config["enabled"] else "NOT_CONFIGURED"
    
    return status

if __name__ == "__main__":
    print("🔍 Observability Integration Status Check")
    print("=" * 50)
    
    status = check_integration_status()
    
    for system, config in status.items():
        print(f"\n📊 {system.upper()}:")
        print(f"   Status: {config['status']}")
        print(f"   Enabled: {config['enabled']}")
        
        if not config['enabled']:
            print(f"   ⚠️  Not configured - check environment variables")
    
    print("\n" + "=" * 50)
    print("📋 Setup Guide:")
    print(get_environment_setup_guide()) 