#!/usr/bin/env python3
"""
Quick fix for manage_services.py indentation issues
"""


def fix_manage_services():
    file_path = "src/utils/manage_services.py"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Fix the indentation issue on line 1821
    if len(lines) >= 1821:
        # Line 1821 should be indented to be inside the for loop
        if "print(line.rstrip())" in lines[1820]:  # Line 1821 is at index 1820
            lines[1820] = "                        print(line.rstrip())\n"

    # Fix the syntax error on line 1951 - remove the else statement
    if len(lines) >= 1951:
        # Line 1951 has an else statement that doesn't belong
        if "        else:" in lines[1950]:  # Line 1951 is at index 1950
            lines[1950] = '        print_info("No active connections found")\n'

    # Write the fixed content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("Fixed manage_services.py indentation issues")


if __name__ == "__main__":
    fix_manage_services()
