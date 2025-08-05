#!/usr/bin/env python3
"""
System setup script that ensures all directories and basic configuration are in place.
Run this script before starting the Sentinel AI system.
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "db", 
        "workspace",
        "static",
        "templates",
        "config",
    ]
    
    print("📁 Setting up directory structure...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")

def setup_gitignore():
    """Create or update .gitignore to exclude sensitive and temporary files"""
    gitignore_content = """
# Environment variables
.env
.env.local
.env.production

# Logs
logs/
*.log

# Database
db/
*.db
*.sqlite

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
*.tmp

# Node modules (if any frontend tooling)
node_modules/

# Workspace files (may contain sensitive data)
workspace/*
!workspace/.gitkeep

# Wandb artifacts
wandb/

# Model cache
.cache/
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    print("✅ Updated .gitignore")

def create_workspace_readme():
    """Create a README in the workspace directory"""
    workspace_readme = """# Workspace Directory

This directory is used by Sentinel AI agents to execute tasks and store temporary files.

## Structure
- Agent-created files will appear here during mission execution
- Each mission may create subdirectories for organization
- Files are automatically cleaned up after mission completion (configurable)

## Security
- This directory is excluded from version control via .gitignore
- Only trusted code should be executed here
- Review any files created by agents before using them in production

## Permissions
The system will create files with standard user permissions.
Ensure this directory has appropriate read/write access for the application.
"""
    
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    with open(workspace_dir / "README.md", "w") as f:
        f.write(workspace_readme.strip())
    
    print("✅ Created workspace/README.md")

def verify_python_version():
    """Verify Python version compatibility"""
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("⚠️  Sentinel AI requires Python 3.8 or higher")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def check_essential_files():
    """Check if essential files exist"""
    essential_files = [
        "src/main.py",
        "requirements.txt",
        "config/settings.py",
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("❌ Missing essential files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Sentinel AI System Setup")
    print("="*40)
    
    # Check Python version
    if not verify_python_version():
        return 1
    
    # Check essential files
    print("\n📋 Checking essential files...")
    if not check_essential_files():
        print("\n❌ Setup cannot continue with missing files")
        return 1
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Setup gitignore
    print("\n🔒 Setting up .gitignore...")
    setup_gitignore()
    
    # Create workspace documentation
    print("\n📝 Setting up workspace...")
    create_workspace_readme()
    
    print("\n" + "="*40)
    print("✅ System setup complete!")
    print("\nNext steps:")
    print("1. Run: python system_optimizer.py")
    print("2. Configure your .env file")
    print("3. Install dependencies: pip install -r requirements.txt") 
    print("4. Start the system: uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload")
    
    return 0

if __name__ == "__main__":
    exit(main())