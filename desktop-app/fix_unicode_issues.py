#!/usr/bin/env python3
"""
Fix Unicode encoding issues in test files
"""

import re

def fix_unicode_in_file(filename):
    """Replace Unicode emoji with ASCII equivalents"""
    
    # Unicode to ASCII mappings
    replacements = {
        "🚀": "[STARTUP]",
        "🧠": "[AI]",
        "🔧": "[TOOL]",
        "✅": "[OK]",
        "❌": "[ERROR]",
        "⚠️": "[WARN]",
        "📊": "[STATS]",
        "📋": "[INFO]",
        "📝": "[ADD]",
        "🎉": "[SUCCESS]",
        "📱": "[APP]",
        "🧪": "[TEST]",
        "🏥": "[HEALTH]",
        "📁": "[FILE]",
        "🌐": "[WEB]",
        "⚡": "[PERF]",
        "🔒": "[SEC]",
        "🗄️": "[DB]",
        "🤖": "[BOT]",
        "🎯": "[TARGET]",
        "⚙️": "[CONFIG]"
    }
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all Unicode emoji
        for unicode_char, ascii_replacement in replacements.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed Unicode encoding in {filename}")
        return True
        
    except Exception as e:
        print(f"Error fixing {filename}: {e}")
        return False

if __name__ == "__main__":
    files_to_fix = [
        "comprehensive_test_suite.py",
        "ai_agent_testing.py",
        "advanced_logging_config.py",
        "run_comprehensive_tests.py"
    ]
    
    for file in files_to_fix:
        fix_unicode_in_file(file) 