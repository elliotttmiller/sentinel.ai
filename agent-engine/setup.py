"""
Setup script for Project Sentinel Agent Engine.

Installs dependencies and configures the environment.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"✗ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    # Install dependencies
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    
    directories = [
        "logs",
        "data",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")
    
    return True


def setup_environment():
    """Setup environment configuration."""
    print("\nSetting up environment...")
    
    env_example = Path("env_example.txt")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("✗ env_example.txt not found")
        return False
    
    if not env_file.exists():
        # Copy example to .env
        import shutil
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from template")
        print("⚠️  Please edit .env file with your actual configuration")
    else:
        print("✓ .env file already exists")
    
    return True


def run_tests():
    """Run setup tests."""
    print("\nRunning setup tests...")
    
    return run_command(
        f"{sys.executable} test_setup.py",
        "Running setup tests"
    )


def main():
    """Main setup function."""
    print("Project Sentinel Agent Engine - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return False
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Could not create directories")
        return False
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Setup failed: Could not setup environment")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return False
    
    # Run tests
    if not run_tests():
        print("\n❌ Setup failed: Tests did not pass")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python main.py")
    print("3. Visit: http://localhost:8001/docs for API documentation")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 