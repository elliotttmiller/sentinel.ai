#!/usr/bin/env python3
"""
System Optimization and Configuration Checker
This script verifies that all components are properly configured and optimized.
"""

import os
import sys
import json
from pathlib import Path

def check_environment_variables():
    """Check if essential environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        ("GOOGLE_API_KEY", "Google API key for LLM access"),
        ("LLM_MODEL", "LLM model name (optional, defaults to gemini-1.5-pro)"),
        ("LLM_TEMPERATURE", "LLM temperature (optional, defaults to 0.7)"),
    ]
    
    optional_vars = [
        ("DATABASE_URL", "Database connection URL"),
        ("SENTRY_DSN", "Sentry error tracking"),
        ("WANDB_API_KEY", "Weights & Biases logging"),
    ]
    
    issues = []
    warnings = []
    
    for var, description in required_vars:
        if not os.getenv(var):
            issues.append(f"❌ Missing required variable: {var} ({description})")
        else:
            print(f"✅ {var} is set")
    
    for var, description in optional_vars:
        if not os.getenv(var):
            warnings.append(f"⚠️  Optional variable not set: {var} ({description})")
        else:
            print(f"✅ {var} is set")
    
    return issues, warnings

def check_file_structure():
    """Check if essential files and directories exist"""
    print("\n📁 Checking file structure...")
    
    essential_files = [
        "src/main.py",
        "src/utils/google_ai_wrapper.py", 
        "src/utils/llm_patch.py",
        "src/utils/litellm_custom_provider.py",
        "src/core/execution_workflow.py",
        "src/agents/executable_agent.py",
        "config/settings.py",
    ]
    
    essential_dirs = [
        "src",
        "config", 
        "workspace",
        "logs",
        "db",
    ]
    
    issues = []
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            issues.append(f"❌ Missing essential file: {file_path}")
    
    for dir_path in essential_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️  Creating missing directory: {dir_path}/")
            os.makedirs(dir_path, exist_ok=True)
    
    return issues

def check_python_dependencies():
    """Check if essential Python packages are available"""
    print("\n📦 Checking Python dependencies...")
    
    essential_packages = [
        ("fastapi", "Web framework"),
        ("uvicorn", "ASGI server"),
        ("crewai", "AI agent framework"),
        ("langchain_google_genai", "Google AI integration"),
        ("loguru", "Logging"),
        ("pydantic", "Data validation"),
        ("python_dotenv", "Environment variables"),
    ]
    
    optional_packages = [
        ("docker", "Containerization"),
        ("wandb", "Experiment tracking"),
        ("weave", "Observability"),
        ("chromadb", "Vector database"),
    ]
    
    issues = []
    warnings = []
    
    for package, description in essential_packages:
        try:
            __import__(package)
            print(f"✅ {package} ({description})")
        except ImportError:
            issues.append(f"❌ Missing essential package: {package} ({description})")
    
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package} ({description})")
        except ImportError:
            warnings.append(f"⚠️  Optional package not available: {package} ({description})")
    
    return issues, warnings

def check_model_name_configuration():
    """Check if the model name is configured correctly"""
    print("\n🤖 Checking LLM model configuration...")
    
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    print(f"📋 Configured model: {model_name}")
    
    # Test the model name formatting logic
    def test_model_format(model):
        """Test model name formatting"""
        if model.startswith("models/gemini"):
            clean_name = model.split('/')[-1]
            result = f"gemini/{clean_name}"
            return result, True
        elif model.startswith("models/"):
            clean_name = model.replace("models/", "")
            result = f"gemini/{clean_name}"
            return result, True
        elif not model.startswith("gemini/"):
            result = f"gemini/{model}"
            return result, True
        else:
            return model, True
    
    formatted_model, is_valid = test_model_format(model_name)
    
    if is_valid:
        print(f"✅ Model name format is valid")
        print(f"📋 LiteLLM format: {formatted_model}")
        return []
    else:
        return [f"❌ Invalid model name format: {model_name}"]

def generate_optimization_report():
    """Generate a comprehensive optimization report"""
    print("\n" + "="*60)
    print("🔧 SYSTEM OPTIMIZATION REPORT")
    print("="*60)
    
    all_issues = []
    all_warnings = []
    
    # Run all checks
    env_issues, env_warnings = check_environment_variables()
    file_issues = check_file_structure()
    dep_issues, dep_warnings = check_python_dependencies()
    model_issues = check_model_name_configuration()
    
    all_issues.extend(env_issues)
    all_issues.extend(file_issues)
    all_issues.extend(dep_issues)
    all_issues.extend(model_issues)
    
    all_warnings.extend(env_warnings)
    all_warnings.extend(dep_warnings)
    
    # Generate summary
    print(f"\n📊 SUMMARY:")
    print(f"Critical Issues: {len(all_issues)}")
    print(f"Warnings: {len(all_warnings)}")
    
    if all_issues:
        print(f"\n❌ CRITICAL ISSUES TO FIX:")
        for issue in all_issues:
            print(f"   {issue}")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS (Optional):")
        for warning in all_warnings:
            print(f"   {warning}")
    
    if not all_issues:
        print(f"\n🎉 System appears to be properly configured!")
        print(f"✅ Ready for mission execution")
        
        print(f"\n🚀 To start the system:")
        print(f"   cd desktop-app")
        print(f"   uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload")
    else:
        print(f"\n⚠️  Please fix the critical issues before starting the system")
    
    return len(all_issues) == 0

def create_env_template():
    """Create a .env template file if it doesn't exist"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"\n📝 Creating {env_file} template...")
        
        template = """# Sentinel AI Configuration
# Copy this file to .env and fill in your actual values

# Required: Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LLM Configuration  
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7

# Optional: Database Configuration
DATABASE_URL=sqlite:///db/sentinel_missions.db

# Optional: Observability
SENTRY_DSN=your_sentry_dsn_here
WANDB_API_KEY=your_wandb_api_key_here

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO
"""
        
        with open(env_file, 'w') as f:
            f.write(template)
        
        print(f"✅ Created {env_file} template")
        print(f"📝 Please edit {env_file} and add your API keys")
        return False
    else:
        return True

def main():
    """Main optimization checker"""
    print("🚀 Sentinel AI System Optimization Checker")
    print("="*60)
    
    # Create .env template if needed
    env_exists = create_env_template()
    
    if not env_exists:
        print(f"\n⚠️  Please configure your .env file first, then run this script again")
        return 1
    
    # Run full optimization check
    success = generate_optimization_report()
    
    print(f"\n" + "="*60)
    if success:
        print("🎉 SYSTEM IS OPTIMIZED AND READY!")
        return 0
    else:
        print("⚠️  SYSTEM NEEDS CONFIGURATION")
        return 1

if __name__ == "__main__":
    exit(main())