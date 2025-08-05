#!/usr/bin/env python3
"""
Check for missing docstrings in key files
"""

import os
import re

def check_file_for_docstrings(filepath):
    """Check a file for missing docstrings in classes and functions"""
    issues = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Find class and function definitions
        for i, line in enumerate(lines):
            # Check for class definitions
            if re.match(r'^\s*class\s+\w+.*:', line):
                class_name = re.search(r'class\s+(\w+)', line).group(1)
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines):
                    next_line = lines[j].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        issues.append(f"Line {i+1}: Class '{class_name}' missing docstring")
            
            # Check for function definitions (excluding __init__ and private methods)
            elif re.match(r'^\s*def\s+\w+.*:', line):
                func_name = re.search(r'def\s+(\w+)', line).group(1)
                if not func_name.startswith('_'):  # Skip private methods
                    # Check if next non-empty line is a docstring
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    if j < len(lines):
                        next_line = lines[j].strip()
                        if not (next_line.startswith('"""') or next_line.startswith("'''")):
                            issues.append(f"Line {i+1}: Function '{func_name}' missing docstring")
        
        return issues
    
    except Exception as e:
        return [f"Error reading {filepath}: {e}"]

def main():
    """Check key files for missing docstrings"""
    key_files = [
        'src/main.py',
        'src/core/cognitive_forge_engine.py',
        'src/utils/google_ai_wrapper.py',
        'src/models/advanced_database.py',
        'src/agents/advanced_agents.py',
        'src/agents/specialized_agents.py'
    ]
    
    print("🔍 Checking for missing docstrings...")
    print("=" * 50)
    
    total_issues = 0
    
    for filepath in key_files:
        if os.path.exists(filepath):
            issues = check_file_for_docstrings(filepath)
            if issues:
                print(f"\n📁 {filepath}:")
                for issue in issues:
                    print(f"  ❌ {issue}")
                total_issues += len(issues)
            else:
                print(f"✅ {filepath}: All major functions/classes have docstrings")
        else:
            print(f"⚠️  {filepath}: File not found")
    
    print("=" * 50)
    print(f"📊 Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("🎉 All key files have proper docstrings!")
    else:
        print("⚠️  Some functions/classes are missing docstrings")
    
    return total_issues == 0

if __name__ == "__main__":
    main()