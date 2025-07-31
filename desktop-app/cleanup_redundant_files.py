#!/usr/bin/env python3
"""
DESKTOP-APP CLEANUP SCRIPT
Removes redundant and unnecessary files to clean up the organization

This script will:
1. Remove duplicate test files
2. Remove redundant documentation
3. Remove redundant startup scripts
4. Clean up old backup directories
5. Clean up old wandb run directories
6. Remove utility files that are no longer needed
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

class DesktopAppCleaner:
    """Cleaner for desktop-app directory"""
    
    def __init__(self):
        self.desktop_app_path = Path(__file__).parent
        self.removed_files = []
        self.removed_dirs = []
        self.errors = []
        
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"🧹 {title}")
        print(f"{'='*80}")
    
    def print_result(self, action: str, status: str, details: str = ""):
        """Print formatted result"""
        status_icon = "✅" if status == "REMOVED" else "❌" if status == "ERROR" else "⚠️"
        print(f"{status_icon} {action}: {status}")
        if details:
            print(f"   📝 {details}")
    
    def remove_file(self, file_path: str, reason: str):
        """Remove a file and track the action"""
        try:
            full_path = self.desktop_app_path / file_path
            if full_path.exists():
                full_path.unlink()
                self.removed_files.append((str(full_path), reason))
                self.print_result(f"File: {file_path}", "REMOVED", reason)
                return True
            else:
                self.print_result(f"File: {file_path}", "SKIPPED", "File not found")
                return False
        except Exception as e:
            self.errors.append(f"Error removing {file_path}: {str(e)}")
            self.print_result(f"File: {file_path}", "ERROR", str(e))
            return False
    
    def remove_directory(self, dir_path: str, reason: str):
        """Remove a directory and track the action"""
        try:
            full_path = self.desktop_app_path / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)
                self.removed_dirs.append((str(full_path), reason))
                self.print_result(f"Directory: {dir_path}", "REMOVED", reason)
                return True
            else:
                self.print_result(f"Directory: {dir_path}", "SKIPPED", "Directory not found")
                return False
        except Exception as e:
            self.errors.append(f"Error removing {dir_path}: {str(e)}")
            self.print_result(f"Directory: {dir_path}", "ERROR", str(e))
            return False
    
    def cleanup_old_backups(self, keep_count: int = 3):
        """Clean up old backup directories, keeping only the latest ones"""
        self.print_header("CLEANING UP OLD BACKUP DIRECTORIES")
        
        backup_dir = self.desktop_app_path / "backups"
        if not backup_dir.exists():
            self.print_result("Backup cleanup", "SKIPPED", "Backups directory not found")
            return
        
        # Find all backup directories
        backup_dirs = []
        for item in backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("fix_ai_backup_"):
                backup_dirs.append(item)
        
        if len(backup_dirs) <= keep_count:
            self.print_result("Backup cleanup", "SKIPPED", f"Only {len(backup_dirs)} backups found, keeping all")
            return
        
        # Sort by modification time (newest first)
        backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for old_backup in backup_dirs[keep_count:]:
            self.remove_directory(f"backups/{old_backup.name}", "Old backup directory")
    
    def cleanup_old_wandb_runs(self, keep_count: int = 3):
        """Clean up old wandb run directories, keeping only the latest ones"""
        self.print_header("CLEANING UP OLD WANDB RUNS")
        
        wandb_dir = self.desktop_app_path / "wandb"
        if not wandb_dir.exists():
            self.print_result("WANDB cleanup", "SKIPPED", "WANDB directory not found")
            return
        
        # Find all run directories
        run_dirs = []
        for item in wandb_dir.iterdir():
            if item.is_dir() and item.name.startswith("run-"):
                run_dirs.append(item)
        
        if len(run_dirs) <= keep_count:
            self.print_result("WANDB cleanup", "SKIPPED", f"Only {len(run_dirs)} runs found, keeping all")
            return
        
        # Sort by modification time (newest first)
        run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old runs
        for old_run in run_dirs[keep_count:]:
            self.remove_directory(f"wandb/{old_run.name}", "Old WANDB run directory")
    
    def cleanup_redundant_test_files(self):
        """Remove redundant test files"""
        self.print_header("REMOVING REDUNDANT TEST FILES")
        
        redundant_tests = [
            ("test_fix_ai_comprehensive.py", "Redundant with comprehensive_system_test.py"),
            ("test_automated_debugging.py", "Functionality covered in comprehensive tests"),
            ("test_sentry_integration.py", "Functionality covered in comprehensive tests"),
            ("test_weave_integration.py", "Functionality covered in comprehensive tests"),
            ("test_performance_demo.py", "Redundant with system optimization hub"),
            ("test_prompt_optimization.py", "Functionality covered in system tests"),
        ]
        
        for test_file, reason in redundant_tests:
            self.remove_file(test_file, reason)
    
    def cleanup_redundant_documentation(self):
        """Remove redundant documentation files"""
        self.print_header("REMOVING REDUNDANT DOCUMENTATION")
        
        redundant_docs = [
            ("WEAVE_INTEGRATION_SUMMARY.md", "Redundant with main README"),
            ("WEAVE_INTEGRATION_DOCUMENTATION.md", "Redundant with main README"),
            ("SYSTEM_OPTIMIZATION_HUB_GUIDE.md", "Redundant with main README"),
            ("CURRENT_VERSION_SUMMARY.md", "Redundant with main README"),
            ("COGNITIVE_FORGE_V5_OPERATIONAL_PROCESS_MAP.md", "Redundant with main README"),
            ("PROMPT_OPTIMIZATION_AGENT_SUMMARY.md", "Redundant with main README"),
            ("DATABASE_CONFIGURATION.md", "Redundant with main README"),
            ("ARCHITECTURAL_PURITY_ACHIEVED.md", "Redundant with main README"),
            ("SYSTEM_STATUS.md", "Redundant with main README"),
            ("OPTIMIZATION_SYSTEM_OVERVIEW.md", "Redundant with main README"),
            ("STARTUP_GUIDE.md", "Redundant with main README"),
            ("DEPLOYMENT_GUIDE.md", "Redundant with main README"),
            ("PERFORMANCE_METRICS_GUIDE.md", "Redundant with main README"),
        ]
        
        for doc_file, reason in redundant_docs:
            self.remove_file(doc_file, reason)
    
    def cleanup_redundant_scripts(self):
        """Remove redundant startup and utility scripts"""
        self.print_header("REMOVING REDUNDANT SCRIPTS")
        
        redundant_scripts = [
            ("start_servers.ps1", "Redundant with start_servers_cursor.ps1"),
            ("start_servers.bat", "Redundant with PowerShell scripts"),
            ("wandb_login.py", "One-time setup script, no longer needed"),
            ("run_optimization_tests.py", "Redundant with system optimization hub"),
            ("init_db_simple.py", "Redundant with main database setup"),
        ]
        
        for script_file, reason in redundant_scripts:
            self.remove_file(script_file, reason)
    
    def cleanup_pycache(self):
        """Remove __pycache__ directories"""
        self.print_header("REMOVING PYTHON CACHE DIRECTORIES")
        
        # Remove root __pycache__
        if (self.desktop_app_path / "__pycache__").exists():
            self.remove_directory("__pycache__", "Python cache directory")
        
        # Find and remove all __pycache__ directories recursively
        for pycache_dir in self.desktop_app_path.rglob("__pycache__"):
            if pycache_dir.is_dir():
                relative_path = pycache_dir.relative_to(self.desktop_app_path)
                self.remove_directory(str(relative_path), "Python cache directory")
    
    def generate_cleanup_report(self):
        """Generate a cleanup report"""
        self.print_header("CLEANUP SUMMARY")
        
        print(f"📁 Files Removed: {len(self.removed_files)}")
        print(f"📁 Directories Removed: {len(self.removed_dirs)}")
        print(f"❌ Errors Encountered: {len(self.errors)}")
        
        if self.removed_files:
            print(f"\n📄 Removed Files:")
            for file_path, reason in self.removed_files:
                print(f"   - {file_path}: {reason}")
        
        if self.removed_dirs:
            print(f"\n📁 Removed Directories:")
            for dir_path, reason in self.removed_dirs:
                print(f"   - {dir_path}: {reason}")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")
        
        # Calculate space saved (approximate)
        total_removed = len(self.removed_files) + len(self.removed_dirs)
        print(f"\n🎉 Cleanup completed! Removed {total_removed} items.")
        
        if not self.errors:
            print("✅ All cleanup operations completed successfully!")
        else:
            print(f"⚠️ Cleanup completed with {len(self.errors)} errors.")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        self.print_header("DESKTOP-APP CLEANUP PROCESS")
        print("🧹 This script will remove redundant and unnecessary files to clean up the organization.")
        print("📋 The following items will be removed:")
        print("   - Duplicate test files")
        print("   - Redundant documentation")
        print("   - Redundant startup scripts")
        print("   - Old backup directories (keeping latest 3)")
        print("   - Old WANDB run directories (keeping latest 3)")
        print("   - Python cache directories")
        print("   - Utility files no longer needed")
        
        # Ask for confirmation
        response = input("\n❓ Do you want to proceed with the cleanup? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Cleanup cancelled by user.")
            return
        
        print("\n🚀 Starting cleanup process...")
        
        # Run cleanup operations
        self.cleanup_redundant_test_files()
        self.cleanup_redundant_documentation()
        self.cleanup_redundant_scripts()
        self.cleanup_old_backups(keep_count=3)
        self.cleanup_old_wandb_runs(keep_count=3)
        self.cleanup_pycache()
        
        # Generate report
        self.generate_cleanup_report()


def main():
    """Main execution function"""
    cleaner = DesktopAppCleaner()
    cleaner.run_cleanup()


if __name__ == "__main__":
    main() 