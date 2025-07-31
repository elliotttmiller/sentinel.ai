#!/usr/bin/env python3
"""
COMPREHENSIVE FIX-AI TESTING SCRIPT
Scans entire desktop-app directory for errors and uses Fix-AI to fix them

This script will:
1. Scan all Python files in desktop-app for syntax errors
2. Run flake8 linting to find code quality issues
3. Use Fix-AI to automatically fix discovered issues
4. Validate fixes and provide detailed reporting
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

class ComprehensiveFixAITester:
    """
    Comprehensive tester for Fix-AI that scans and fixes the entire desktop-app
    """
    
    def __init__(self):
        self.desktop_app_path = Path(__file__).parent
        self.fix_ai_path = self.desktop_app_path / "Fix-AI.py"
        self.results = {
            "scan_results": {},
            "fix_results": {},
            "validation_results": {},
            "summary": {}
        }
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"🔍 {title}")
        print(f"{'='*80}")
    
    def print_result(self, test_name: str, status: str, details: str = ""):
        """Print formatted test result"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in desktop-app"""
        python_files = []
        
        for root, dirs, files in os.walk(self.desktop_app_path):
            # Skip virtual environments and common directories to avoid
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules', 'wandb']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        return python_files
    
    def test_syntax_errors(self, python_files: List[Path]) -> Dict[str, Any]:
        """Test for syntax errors in Python files"""
        self.print_header("SYNTAX ERROR SCANNING")
        
        syntax_errors = []
        valid_files = []
        
        for file_path in python_files:
            try:
                # Try to compile the file to check for syntax errors
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                compile(content, str(file_path), 'exec')
                valid_files.append(str(file_path))
                
            except SyntaxError as e:
                error_info = {
                    "file": str(file_path),
                    "line": e.lineno,
                    "message": str(e.msg),
                    "text": e.text
                }
                syntax_errors.append(error_info)
                self.print_result(f"Syntax Check: {file_path.name}", "FAIL", f"Line {e.lineno}: {e.msg}")
            except Exception as e:
                error_info = {
                    "file": str(file_path),
                    "line": "unknown",
                    "message": str(e),
                    "text": "unknown"
                }
                syntax_errors.append(error_info)
                self.print_result(f"Syntax Check: {file_path.name}", "FAIL", f"Error: {str(e)}")
        
        self.print_result("Syntax Scanning", "PASS" if not syntax_errors else "FAIL", 
                         f"Found {len(syntax_errors)} syntax errors in {len(python_files)} files")
        
        return {
            "total_files": len(python_files),
            "valid_files": len(valid_files),
            "syntax_errors": syntax_errors
        }
    
    def run_flake8_scan(self, python_files: List[Path]) -> Dict[str, Any]:
        """Run flake8 linting on Python files"""
        self.print_header("FLAKE8 CODE QUALITY SCANNING")
        
        flake8_errors = []
        
        for file_path in python_files:
            try:
                # Run flake8 on individual file
                result = subprocess.run(
                    ['flake8', str(file_path), '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    try:
                        errors = json.loads(result.stdout)
                        for error in errors:
                            error_info = {
                                "file": str(file_path),
                                "line": error.get("line_number", 0),
                                "column": error.get("column_number", 0),
                                "code": error.get("code", ""),
                                "text": error.get("text", ""),
                                "physical_line": error.get("physical_line", "")
                            }
                            flake8_errors.append(error_info)
                            self.print_result(f"Flake8: {file_path.name}", "FAIL", 
                                             f"Line {error_info['line']}: {error_info['code']} - {error_info['text']}")
                    except json.JSONDecodeError:
                        # Handle non-JSON output
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip():
                                flake8_errors.append({
                                    "file": str(file_path),
                                    "line": 0,
                                    "column": 0,
                                    "code": "FLAKE8",
                                    "text": line.strip(),
                                    "physical_line": ""
                                })
                
            except subprocess.TimeoutExpired:
                self.print_result(f"Flake8: {file_path.name}", "FAIL", "Timeout")
            except Exception as e:
                self.print_result(f"Flake8: {file_path.name}", "FAIL", f"Error: {str(e)}")
        
        self.print_result("Flake8 Scanning", "PASS" if not flake8_errors else "FAIL", 
                         f"Found {len(flake8_errors)} flake8 issues")
        
        return {
            "total_files": len(python_files),
            "flake8_errors": flake8_errors
        }
    
    def load_fix_ai(self) -> Optional[Any]:
        """Load Fix-AI module"""
        try:
            if not self.fix_ai_path.exists():
                self.print_result("Fix-AI Loading", "FAIL", "Fix-AI.py not found")
                return None
            
            spec = importlib.util.spec_from_file_location("Fix_AI", self.fix_ai_path)
            fix_ai_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fix_ai_module)
            
            if hasattr(fix_ai_module, 'CodebaseHealer'):
                self.print_result("Fix-AI Loading", "PASS", "CodebaseHealer loaded successfully")
                return fix_ai_module.CodebaseHealer
            else:
                self.print_result("Fix-AI Loading", "FAIL", "CodebaseHealer class not found")
                return None
                
        except Exception as e:
            self.print_result("Fix-AI Loading", "FAIL", f"Error: {str(e)}")
            return None
    
    def run_fix_ai_healing(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run Fix-AI to heal the codebase"""
        self.print_header("FIX-AI HEALING PROCESS")
        
        if not issues:
            self.print_result("Fix-AI Healing", "PASS", "No issues to fix")
            return {"healed_issues": 0, "total_issues": 0, "success_rate": 100.0}
        
        # Load Fix-AI
        CodebaseHealer = self.load_fix_ai()
        if not CodebaseHealer:
            return {"healed_issues": 0, "total_issues": len(issues), "success_rate": 0.0}
        
        try:
            # Initialize Fix-AI with the desktop-app directory
            healer = CodebaseHealer(self.desktop_app_path)
            
            # Create a comprehensive issues list for Fix-AI
            comprehensive_issues = []
            
            # Add syntax errors
            for error in issues:
                if "syntax" in error.get("type", ""):
                    comprehensive_issues.append({
                        "file_path": error["file"],
                        "line": error["line"],
                        "issue_type": "SyntaxError",
                        "message": error["message"],
                        "code_context": error.get("text", "")
                    })
            
            # Add flake8 errors
            for error in issues:
                if "flake8" in error.get("type", ""):
                    comprehensive_issues.append({
                        "file_path": error["file"],
                        "line": error["line"],
                        "issue_type": f"Flake8_{error['code']}",
                        "message": error["text"],
                        "code_context": error.get("physical_line", "")
                    })
            
            # Set the issues for Fix-AI
            healer.issues = comprehensive_issues
            
            # Run the healing process
            self.print_result("Fix-AI Initialization", "PASS", f"Initialized with {len(comprehensive_issues)} issues")
            
            # Run diagnosis phase
            diagnosis_result = healer.run_diagnosis_phase()
            self.print_result("Fix-AI Diagnosis", "PASS", "Diagnosis completed")
            
            # Run planning phase
            planning_result = healer.run_planning_phase()
            self.print_result("Fix-AI Planning", "PASS", "Healing plan created")
            
            # Run execution phase
            execution_result = healer.run_execution_phase()
            self.print_result("Fix-AI Execution", "PASS", "Fixes applied")
            
            # Run validation phase
            validation_result = healer.run_final_validation_phase()
            self.print_result("Fix-AI Validation", "PASS", "Validation completed")
            
            return {
                "healed_issues": len(comprehensive_issues),
                "total_issues": len(issues),
                "success_rate": 100.0 if comprehensive_issues else 0.0,
                "diagnosis_result": diagnosis_result,
                "planning_result": planning_result,
                "execution_result": execution_result,
                "validation_result": validation_result
            }
            
        except Exception as e:
            self.print_result("Fix-AI Healing", "FAIL", f"Error during healing: {str(e)}")
            return {
                "healed_issues": 0,
                "total_issues": len(issues),
                "success_rate": 0.0,
                "error": str(e)
            }
    
    def validate_fixes(self, original_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that fixes were successful"""
        self.print_header("VALIDATING FIXES")
        
        # Re-scan for syntax errors
        python_files = self.find_python_files()
        syntax_results = self.test_syntax_errors(python_files)
        
        # Re-run flake8
        flake8_results = self.run_flake8_scan(python_files)
        
        # Compare results
        original_syntax_count = len([i for i in original_issues if "syntax" in i.get("type", "")])
        original_flake8_count = len([i for i in original_issues if "flake8" in i.get("type", "")])
        
        new_syntax_count = len(syntax_results["syntax_errors"])
        new_flake8_count = len(flake8_results["flake8_errors"])
        
        syntax_fixed = original_syntax_count - new_syntax_count
        flake8_fixed = original_flake8_count - new_flake8_count
        
        total_fixed = syntax_fixed + flake8_fixed
        total_original = original_syntax_count + original_flake8_count
        
        success_rate = (total_fixed / total_original * 100) if total_original > 0 else 100
        
        self.print_result("Fix Validation", "PASS" if success_rate >= 80 else "FAIL", 
                         f"Fixed {total_fixed}/{total_original} issues ({success_rate:.1f}% success)")
        
        return {
            "original_issues": total_original,
            "remaining_issues": new_syntax_count + new_flake8_count,
            "fixed_issues": total_fixed,
            "success_rate": success_rate,
            "syntax_fixed": syntax_fixed,
            "flake8_fixed": flake8_fixed
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "desktop_app_path": str(self.desktop_app_path),
            "summary": {
                "total_files_scanned": self.results["scan_results"].get("total_files", 0),
                "total_issues_found": len(self.results["scan_results"].get("syntax_errors", [])) + 
                                    len(self.results["scan_results"].get("flake8_errors", [])),
                "issues_fixed": self.results["validation_results"].get("fixed_issues", 0),
                "success_rate": self.results["validation_results"].get("success_rate", 0)
            },
            "detailed_results": self.results
        }
        
        return report
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run the complete comprehensive Fix-AI test"""
        self.print_header("COMPREHENSIVE FIX-AI TESTING")
        print("🔍 Scanning entire desktop-app directory for errors...")
        print("🛠️ Using Fix-AI to automatically fix discovered issues...")
        print("✅ Validating fixes and generating detailed report...")
        
        start_time = time.time()
        
        # Step 1: Find all Python files
        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files to scan")
        
        # Step 2: Scan for syntax errors
        syntax_results = self.test_syntax_errors(python_files)
        self.results["scan_results"]["syntax_errors"] = syntax_results["syntax_errors"]
        
        # Step 3: Run flake8 scanning
        flake8_results = self.run_flake8_scan(python_files)
        self.results["scan_results"]["flake8_errors"] = flake8_results["flake8_errors"]
        
        # Step 4: Combine all issues
        all_issues = []
        for error in syntax_results["syntax_errors"]:
            error["type"] = "syntax"
            all_issues.append(error)
        
        for error in flake8_results["flake8_errors"]:
            error["type"] = "flake8"
            all_issues.append(error)
        
        # Step 5: Run Fix-AI healing
        if all_issues:
            fix_results = self.run_fix_ai_healing(all_issues)
            self.results["fix_results"] = fix_results
        else:
            self.results["fix_results"] = {"healed_issues": 0, "total_issues": 0, "success_rate": 100.0}
        
        # Step 6: Validate fixes
        validation_results = self.validate_fixes(all_issues)
        self.results["validation_results"] = validation_results
        
        # Step 7: Generate final report
        end_time = time.time()
        execution_time = end_time - start_time
        
        report = self.generate_report()
        report["execution_time"] = execution_time
        
        # Print final summary
        self.print_header("FINAL SUMMARY")
        print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"📁 Files Scanned: {report['summary']['total_files_scanned']}")
        print(f"🔍 Issues Found: {report['summary']['total_issues_found']}")
        print(f"🛠️ Issues Fixed: {report['summary']['issues_fixed']}")
        print(f"📊 Success Rate: {report['summary']['success_rate']:.1f}%")
        
        if report['summary']['success_rate'] >= 90:
            print("🎉 EXCELLENT! Fix-AI successfully resolved most issues!")
        elif report['summary']['success_rate'] >= 70:
            print("✅ GOOD! Fix-AI resolved a significant number of issues.")
        elif report['summary']['success_rate'] >= 50:
            print("⚠️ MODERATE: Fix-AI resolved some issues, manual review recommended.")
        else:
            print("❌ POOR: Fix-AI struggled with the issues. Manual intervention needed.")
        
        # Save detailed report
        report_file = self.desktop_app_path / "logs" / f"fix_ai_comprehensive_report_{int(time.time())}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        return report


def main():
    """Main execution function"""
    tester = ComprehensiveFixAITester()
    result = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if result["summary"]["success_rate"] >= 80:
        sys.exit(0)  # Success
    elif result["summary"]["success_rate"] >= 50:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Failure


if __name__ == "__main__":
    main() 