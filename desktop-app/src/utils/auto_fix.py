#!/usr/bin/env python3
"""
Sentinel Desktop App Auto-Fixer
Automatically checks and fixes Python syntax errors, formatting issues, and import problems.
Similar to npx ts-autofix but for Python.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import json


class PythonAutoFixer:
    """Comprehensive Python syntax and style auto-fixer."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.python_files = []
        self.issues_found = []
        self.fixes_applied = []

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project directory."""
        python_files = []
        for file_path in self.project_dir.rglob("*.py"):
            if "venv" not in str(file_path) and "__pycache__" not in str(file_path):
                python_files.append(file_path)
        return python_files

    def check_syntax(self, file_path: Path) -> Dict[str, Any]:
        """Check Python syntax using ast module."""
        import ast

        result = {"file": str(file_path), "valid": True, "errors": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try to parse the AST
            ast.parse(content)

        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(
                {"type": "SyntaxError", "line": e.lineno, "message": str(e), "text": e.text}
            )
        except Exception as e:
            result["valid"] = False
            result["errors"].append({"type": "Error", "message": str(e)})

        return result

    def format_with_black(self, file_path: Path) -> Dict[str, Any]:
        """Format code using Black."""
        result = {"file": str(file_path), "formatted": False, "error": None}

        try:
            # Run black in check mode first
            check_result = subprocess.run(
                ["black", "--check", "--quiet", str(file_path)], capture_output=True, text=True
            )

            if check_result.returncode != 0:
                # File needs formatting, run black
                format_result = subprocess.run(
                    ["black", "--quiet", str(file_path)], capture_output=True, text=True
                )

                if format_result.returncode == 0:
                    result["formatted"] = True
                else:
                    result["error"] = format_result.stderr
            else:
                result["formatted"] = True  # Already formatted

        except Exception as e:
            result["error"] = str(e)

        return result

    def fix_imports_with_autopep8(self, file_path: Path) -> Dict[str, Any]:
        """Fix imports and basic formatting with autopep8."""
        result = {"file": str(file_path), "fixed": False, "error": None}

        try:
            # Run autopep8 to fix imports and basic issues
            fix_result = subprocess.run(
                ["autopep8", "--in-place", "--aggressive", "--aggressive", str(file_path)],
                capture_output=True,
                text=True,
            )

            if fix_result.returncode == 0:
                result["fixed"] = True
            else:
                result["error"] = fix_result.stderr

        except Exception as e:
            result["error"] = str(e)

        return result

    def lint_with_flake8(self, file_path: Path) -> Dict[str, Any]:
        """Run flake8 linting."""
        result = {"file": str(file_path), "issues": [], "error": None}

        try:
            lint_result = subprocess.run(
                ["flake8", "--max-line-length=100", "--ignore=E501,W503", str(file_path)],
                capture_output=True,
                text=True,
            )

            if lint_result.stdout:
                result["issues"] = lint_result.stdout.strip().split("\n")

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_imports(self, file_path: Path) -> Dict[str, Any]:
        """Check for import issues."""
        result = {"file": str(file_path), "imports": [], "missing": [], "unused": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple import detection
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith(("import ", "from ")):
                    result["imports"].append({"line": i, "import": line})

        except Exception as e:
            result["error"] = str(e)

        return result

    def auto_fix_file(self, file_path: Path) -> Dict[str, Any]:
        """Apply all auto-fixes to a single file."""
        print(f"🔧 Auto-fixing: {file_path.name}")

        result = {
            "file": str(file_path),
            "syntax_valid": False,
            "formatted": False,
            "imports_fixed": False,
            "lint_issues": [],
            "errors": [],
        }

        # Step 1: Check syntax
        syntax_result = self.check_syntax(file_path)
        result["syntax_valid"] = syntax_result["valid"]

        if not syntax_result["valid"]:
            result["errors"].extend(syntax_result["errors"])
            print(f"❌ Syntax errors found in {file_path.name}")
            for error in syntax_result["errors"]:
                print(f"   Line {error.get('line', '?')}: {error['message']}")
            return result

        # Step 2: Fix imports and basic formatting
        autopep8_result = self.fix_imports_with_autopep8(file_path)
        result["imports_fixed"] = autopep8_result["fixed"]

        if autopep8_result["error"]:
            result["errors"].append(f"autopep8 error: {autopep8_result['error']}")

        # Step 3: Format with Black
        black_result = self.format_with_black(file_path)
        result["formatted"] = black_result["formatted"]

        if black_result["error"]:
            result["errors"].append(f"black error: {black_result['error']}")

        # Step 4: Check linting issues
        flake8_result = self.lint_with_flake8(file_path)
        result["lint_issues"] = flake8_result["issues"]

        if flake8_result["error"]:
            result["errors"].append(f"flake8 error: {flake8_result['error']}")

        # Step 5: Final syntax check
        final_syntax = self.check_syntax(file_path)
        if final_syntax["valid"]:
            print(f"✅ {file_path.name} - Auto-fix completed successfully")
        else:
            print(f"❌ {file_path.name} - Still has syntax errors after auto-fix")
            result["errors"].extend(final_syntax["errors"])

        return result

    def auto_fix_project(self) -> Dict[str, Any]:
        """Apply auto-fixes to all Python files in the project."""
        print("🚀 Starting Python Auto-Fix Process...")
        print("=" * 50)

        # Find all Python files
        self.python_files = self.find_python_files()
        print(f"📁 Found {len(self.python_files)} Python files")

        results = {
            "total_files": len(self.python_files),
            "files_processed": 0,
            "files_fixed": 0,
            "files_with_errors": 0,
            "total_errors": 0,
            "file_results": [],
        }

        for file_path in self.python_files:
            try:
                file_result = self.auto_fix_file(file_path)
                results["file_results"].append(file_result)
                results["files_processed"] += 1

                if file_result["syntax_valid"] and not file_result["errors"]:
                    results["files_fixed"] += 1
                else:
                    results["files_with_errors"] += 1
                    results["total_errors"] += len(file_result["errors"])

            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                results["files_with_errors"] += 1
                results["total_errors"] += 1

        # Print summary
        print("\n" + "=" * 50)
        print("📊 Auto-Fix Summary:")
        print(f"   Total files: {results['total_files']}")
        print(f"   Files processed: {results['files_processed']}")
        print(f"   Files fixed: {results['files_fixed']}")
        print(f"   Files with errors: {results['files_with_errors']}")
        print(f"   Total errors: {results['total_errors']}")

        if results["files_with_errors"] == 0:
            print("🎉 All files are now syntax-correct and properly formatted!")
        else:
            print("⚠️  Some files still have issues that need manual attention.")

        return results

    def create_config_files(self):
        """Create configuration files for the tools."""
        # Black configuration
        pyproject_toml = """[tool.black]
line-length = 100
target-version = ['py39']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''
"""

        # Flake8 configuration
        setup_cfg = """[flake8]
max-line-length = 100
ignore = E501,W503,E203,W291,W292,W293
exclude = .git,__pycache__,build,dist,*.egg-info,.venv,venv
"""

        # Write config files
        with open(self.project_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_toml)

        with open(self.project_dir / "setup.cfg", "w") as f:
            f.write(setup_cfg)

        print("📝 Created configuration files for Black and Flake8")


def main():
    """Main entry point."""
    project_dir = Path.cwd()

    print("🐍 Python Auto-Fixer (Similar to npx ts-autofix)")
    print("=" * 50)

    # Create auto-fixer instance
    auto_fixer = PythonAutoFixer(project_dir)

    # Create config files if they don't exist
    if not (project_dir / "pyproject.toml").exists():
        auto_fixer.create_config_files()

    # Run auto-fix
    results = auto_fixer.auto_fix_project()

    # Exit with appropriate code
    if results["files_with_errors"] == 0:
        print("\n✅ Auto-fix completed successfully!")
        sys.exit(0)
    else:
        print(
            f"\n⚠️  Auto-fix completed with {results['files_with_errors']} files still having issues."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
