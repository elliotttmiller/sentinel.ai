#!/usr/bin/env python3
"""
Fix Unicode encoding issues by replacing emoji with ASCII equivalents
"""

import re

def fix_unicode_in_file(filename):
    """Replace Unicode emoji with ASCII equivalents"""
    
    # Unicode to ASCII mappings
    replacements = {
        "🔧": "[FIX]",
        "✅": "[OK]",
        "❌": "[ERROR]",
        "⚠️": "[WARN]",
        "📋": "[INFO]",
        "📝": "[ADD]",
        "🎉": "[SUCCESS]",
        "📱": "[APP]",
        "🧪": "[TEST]"
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
    fix_unicode_in_file("fix_database_schema.py") 