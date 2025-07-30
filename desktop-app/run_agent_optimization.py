#!/usr/bin/env python3
"""
Comprehensive Agent Optimization Runner
Runs all AI agent optimization, fine-tuning, and self-learning systems
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

def run_optimization_suite():
    """Run the complete agent optimization suite"""
    print("🧠 COMPREHENSIVE AI AGENT OPTIMIZATION SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Step 1: AI Agent Optimizer
    print("🔧 STEP 1: AI Agent Optimizer")
    print("-" * 40)
    try:
        from ai_agent_optimizer import main as run_optimizer
        run_optimizer()
        results['optimizer'] = 'SUCCESS'
        print("✅ AI Agent Optimizer completed successfully")
    except Exception as e:
        results['optimizer'] = f'FAILED: {str(e)}'
        print(f"❌ AI Agent Optimizer failed: {e}")
    print()
    
    # Step 2: Live Agent Monitor
    print("📊 STEP 2: Live Agent Monitor")
    print("-" * 40)
    try:
        from live_agent_monitor import main as run_monitor
        run_monitor()
        results['monitor'] = 'SUCCESS'
        print("✅ Live Agent Monitor completed successfully")
    except Exception as e:
        results['monitor'] = f'FAILED: {str(e)}'
        print(f"❌ Live Agent Monitor failed: {e}")
    print()
    
    # Step 3: Agent Self-Learning
    print("🧠 STEP 3: Agent Self-Learning")
    print("-" * 40)
    try:
        from agent_self_learning import main as run_learning
        run_learning()
        results['learning'] = 'SUCCESS'
        print("✅ Agent Self-Learning completed successfully")
    except Exception as e:
        results['learning'] = f'FAILED: {str(e)}'
        print(f"❌ Agent Self-Learning failed: {e}")
    print()
    
    # Step 4: Generate Comprehensive Report
    print("📋 STEP 4: Generating Comprehensive Report")
    print("-" * 40)
    generate_comprehensive_report(results)
    
    print("\n🎉 COMPREHENSIVE OPTIMIZATION SUITE COMPLETED!")
    print("=" * 70)
    
    # Display summary
    print("\n📊 OPTIMIZATION SUMMARY:")
    print("-" * 30)
    for component, result in results.items():
        status = "✅ SUCCESS" if result == 'SUCCESS' else f"❌ {result}"
        print(f"   {component.replace('_', ' ').title()}: {status}")
    
    print(f"\n📁 Check generated files for detailed analysis:")
    print("   - optimization_data_*.json")
    print("   - optimization_report_*.md")
    print("   - live_monitoring_report_*.json")
    print("   - self_learning_report_*.json")
    print("   - comprehensive_optimization_report_*.json")

def generate_comprehensive_report(results: Dict[str, str]):
    """Generate a comprehensive optimization report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"comprehensive_optimization_report_{timestamp}.json"
    
    # Collect all available reports
    report_data = {
        'timestamp': timestamp,
        'optimization_results': results,
        'summary': {
            'total_components': len(results),
            'successful_components': sum(1 for r in results.values() if r == 'SUCCESS'),
            'failed_components': sum(1 for r in results.values() if r != 'SUCCESS')
        },
        'recommendations': generate_recommendations(results)
    }
    
    # Try to include data from individual reports
    try:
        # Look for optimization data
        import glob
        optimization_files = glob.glob("optimization_data_*.json")
        if optimization_files:
            with open(optimization_files[-1], 'r') as f:
                report_data['optimization_data'] = json.load(f)
        
        # Look for monitoring data
        monitoring_files = glob.glob("live_monitoring_report_*.json")
        if monitoring_files:
            with open(monitoring_files[-1], 'r') as f:
                report_data['monitoring_data'] = json.load(f)
        
        # Look for learning data
        learning_files = glob.glob("self_learning_report_*.json")
        if learning_files:
            with open(learning_files[-1], 'r') as f:
                report_data['learning_data'] = json.load(f)
                
    except Exception as e:
        print(f"⚠️ Warning: Could not include individual report data: {e}")
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"✅ Comprehensive report saved to: {report_file}")

def generate_recommendations(results: Dict[str, str]) -> List[str]:
    """Generate recommendations based on optimization results"""
    recommendations = []
    
    if results.get('optimizer') == 'SUCCESS':
        recommendations.append("✅ Agent optimization completed - review performance metrics")
        recommendations.append("📊 Analyze agent strengths and weaknesses from optimization data")
        recommendations.append("🎯 Focus on improving agents with low success rates")
    
    if results.get('monitor') == 'SUCCESS':
        recommendations.append("✅ Live monitoring completed - review thinking processes")
        recommendations.append("🧠 Analyze agent decision-making patterns")
        recommendations.append("💡 Identify areas where agents need better reasoning")
    
    if results.get('learning') == 'SUCCESS':
        recommendations.append("✅ Self-learning completed - review improvement suggestions")
        recommendations.append("🔧 Apply high-priority improvements to agent configurations")
        recommendations.append("🔄 Implement continuous learning cycles")
    
    # General recommendations
    if all(r == 'SUCCESS' for r in results.values()):
        recommendations.append("🎉 All systems completed successfully!")
        recommendations.append("🚀 Consider implementing automated optimization cycles")
        recommendations.append("📈 Monitor agent performance improvements over time")
    else:
        recommendations.append("⚠️ Some components failed - review error logs")
        recommendations.append("🔧 Fix failed components before next optimization cycle")
    
    return recommendations

def run_quick_test():
    """Run a quick test to verify the system is working"""
    print("🧪 QUICK SYSTEM TEST")
    print("=" * 30)
    
    try:
        # Test basic imports
        print("📦 Testing imports...")
        from ai_agent_optimizer import AIAgentOptimizer
        from live_agent_monitor import LiveAgentMonitor
        from agent_self_learning import AgentSelfLearning
        print("✅ All imports successful")
        
        # Test agent creation
        print("🤖 Testing agent creation...")
        optimizer = AIAgentOptimizer()
        monitor = LiveAgentMonitor()
        learner = AgentSelfLearning()
        print("✅ Agent systems initialized")
        
        # Test API connection
        print("🔌 Testing API connection...")
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
        else:
            print(f"⚠️ API connection issue: {response.status_code}")
        
        print("\n✅ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main optimization runner"""
    print("🧠 AI Agent Optimization & Fine-Tuning System")
    print("=" * 60)
    
    # Check if desktop app is running
    print("🔍 Checking system status...")
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            print("⚠️ Desktop app may not be running. Please start it first:")
            print("   python -m uvicorn src.main:app --host 0.0.0.0 --port 8001")
            return
        print("✅ Desktop app is running")
    except:
        print("❌ Cannot connect to desktop app. Please start it first.")
        return
    
    # Run quick test
    if not run_quick_test():
        print("❌ System test failed. Please check dependencies.")
        return
    
    print("\n🚀 Starting comprehensive optimization suite...")
    print("This will take several minutes to complete.")
    print()
    
    # Run the full optimization suite
    run_optimization_suite()

if __name__ == "__main__":
    main() 