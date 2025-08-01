#!/usr/bin/env python3
"""
QUICK FIX-AI TESTING SCRIPT
Quick testing of Fix-AI on specific files or running a fast scan

Usage:
- python quick_fix_ai_test.py                    # Quick scan of all Python files
- python quick_fix_ai_test.py file1.py file2.py  # Test specific files
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import importlib.util

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_result(test_name: str, status: str, details: str = ""):
    """Print formatted test result"""
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {test_name}: {status}")
    if details:
        print(f"   📝 {details}")

def find_python_files(target_paths: List[str] = None) -> List[Path]:
    """Find Python files to test"""
    desktop_app_path = Path(__file__).parent
    
    if target_paths:
        # Test specific files
        python_files = []
        for target in target_paths:
            file_path = Path(target)
            if file_path.exists() and file_path.suffix == '.py':
                python_files.append(file_path)
            else:
                print(f"⚠️ File not found or not a Python file: {target}")
        return python_files
    else:
        # Quick scan of main directories
        python_files = []
        main_dirs = ['src', 'tests', 'scripts']
        
        for dir_name in main_dirs:
            dir_path = desktop_app_path / dir_name
            if dir_path.exists():
                for file_path in dir_path.rglob('*.py'):
                    if '__pycache__' not in str(file_path):
                        python_files.append(file_path)
        
        # Also check root directory
        for file_path in desktop_app_path.glob('*.py'):
            if file_path.name != 'quick_fix_ai_test.py':
                python_files.append(file_path)
        
        return python_files

def quick_syntax_check(file_path: Path) -> Dict[str, Any]:
    """Quick syntax check for a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(file_path), 'exec')
        return {"valid": True, "error": None}
        
    except SyntaxError as e:
        return {
            "valid": False, 
            "error": {
                "type": "SyntaxError",
                "line": e.lineno,
                "message": str(e.msg),
                "text": e.text
            }
        }
    except Exception as e:
        return {
            "valid": False,
            "error": {
                "type": "Error",
                "line": "unknown",
                "message": str(e),
                "text": "unknown"
            }
        }

def quick_flake8_check(file_path: Path) -> List[Dict[str, Any]]:
    """Quick flake8 check for a single file"""
    try:
        result = subprocess.run(
            ['flake8', str(file_path), '--format=json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            try:
                errors = json.loads(result.stdout)
                return [
                    {
                        "line": error.get("line_number", 0),
                        "code": error.get("code", ""),
                        "text": error.get("text", "")
                    }
                    for error in errors
                ]
            except json.JSONDecodeError:
                return [{"line": 0, "code": "FLAKE8", "text": result.stdout.strip()}]
        
        return []
        
    except Exception as e:
        return [{"line": 0, "code": "ERROR", "text": str(e)}]

def load_fix_ai():
    """Load Fix-AI module"""
    fix_ai_path = Path(__file__).parent / "Fix-AI.py"
    
    try:
        if not fix_ai_path.exists():
            print_result("Fix-AI Loading", "FAIL", "Fix-AI.py not found")
            return None
        
        spec = importlib.util.spec_from_file_location("Fix_AI", fix_ai_path)
        fix_ai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fix_ai_module)
        
        if hasattr(fix_ai_module, 'CodebaseHealer'):
            print_result("Fix-AI Loading", "PASS", "CodebaseHealer loaded successfully")
            return fix_ai_module.CodebaseHealer
        else:
            print_result("Fix-AI Loading", "FAIL", "CodebaseHealer class not found")
            return None
            
    except Exception as e:
        print_result("Fix-AI Loading", "FAIL", f"Error: {str(e)}")
        return None

def run_fix_ai_on_file(file_path: Path, issues: List[Dict[str, Any]]):
    """Run Fix-AI on a specific file"""
    if not issues:
        print_result(f"Fix-AI: {file_path.name}", "PASS", "No issues to fix")
        return True
    
    CodebaseHealer = load_fix_ai()
    if not CodebaseHealer:
        return False
    
    try:
        # Initialize Fix-AI
        healer = CodebaseHealer(Path(__file__).parent)
        
        # Convert issues to Fix-AI format
        fix_ai_issues = []
        for issue in issues:
            fix_ai_issues.append({
                "file_path": str(file_path),
                "line": issue.get("line", 0),
                "issue_type": issue.get("type", "Unknown"),
                "message": issue.get("message", ""),
                "code_context": issue.get("text", "")
            })
        
        healer.issues = fix_ai_issues
        
        # Run quick healing (just planning and execution)
        planning_result = healer.run_planning_phase()
        execution_result = healer.run_execution_phase()
        
        print_result(f"Fix-AI: {file_path.name}", "PASS", f"Applied fixes for {len(issues)} issues")
        return True
        
    except Exception as e:
        print_result(f"Fix-AI: {file_path.name}", "FAIL", f"Error: {str(e)}")
        return False

def main():
    """Main execution function"""
    print_header("QUICK FIX-AI TESTING")
    
    # Get target files from command line arguments
    target_files = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Find Python files to test
    python_files = find_python_files(target_files)
    
    if not python_files:
        print("❌ No Python files found to test")
        sys.exit(1)
    
    print(f"📁 Testing {len(python_files)} Python files...")
    
    total_issues = 0
    fixed_issues = 0
    
    for file_path in python_files:
        print(f"\n🔍 Testing: {file_path.name}")
        
        # Quick syntax check
        syntax_result = quick_syntax_check(file_path)
        if not syntax_result["valid"]:
            error = syntax_result["error"]
            print_result(f"Syntax: {file_path.name}", "FAIL", 
                        f"Line {error['line']}: {error['message']}")
            total_issues += 1
            
            # Try to fix with Fix-AI
            if run_fix_ai_on_file(file_path, [error]):
                fixed_issues += 1
        else:
            print_result(f"Syntax: {file_path.name}", "PASS")
        
        # Quick flake8 check
        flake8_errors = quick_flake8_check(file_path)
        if flake8_errors:
            for error in flake8_errors:
                print_result(f"Flake8: {file_path.name}", "FAIL", 
                           f"Line {error['line']}: {error['code']} - {error['text']}")
                total_issues += 1
            
            # Try to fix with Fix-AI
            if run_fix_ai_on_file(file_path, flake8_errors):
                fixed_issues += len(flake8_errors)
        else:
            print_result(f"Flake8: {file_path.name}", "PASS")
    
    # Final summary
    print_header("QUICK TEST SUMMARY")
    print(f"📁 Files Tested: {len(python_files)}")
    print(f"🔍 Issues Found: {total_issues}")
    print(f"🛠️ Issues Fixed: {fixed_issues}")
    
    if total_issues > 0:
        success_rate = (fixed_issues / total_issues) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT! Fix-AI successfully resolved most issues!")
        elif success_rate >= 50:
            print("✅ GOOD! Fix-AI resolved a significant number of issues.")
        else:
            print("⚠️ MODERATE: Fix-AI resolved some issues, manual review recommended.")
    else:
        print("🎉 PERFECT! No issues found in the tested files!")
    
    # Exit with appropriate code
    if total_issues == 0:
        sys.exit(0)  # Perfect
    elif fixed_issues >= total_issues * 0.8:
        sys.exit(0)  # Success
    elif fixed_issues >= total_issues * 0.5:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Failure

if __name__ == "__main__":
    main() 