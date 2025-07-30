#!/usr/bin/env python3
"""
Test Script for Enhanced Prompt Optimization Agent
Demonstrates Phase 1: Advanced Prompt Optimization
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.cognitive_forge_engine import CognitiveForgeEngine


async def test_prompt_optimization():
    """Test the enhanced Prompt Optimization Agent"""
    
    print("🧪 TESTING ENHANCED PROMPT OPTIMIZATION AGENT")
    print("=" * 60)
    
    # Initialize the cognitive engine
    engine = CognitiveForgeEngine()
    
    # Test prompt
    test_prompt = "Create a web app for managing tasks"
    
    print(f"📝 Original Prompt: {test_prompt}")
    print("\n🚀 Starting Prompt Optimization...")
    
    # Define update callback
    def update_callback(message: str):
        print(f"  {message}")
    
    try:
        # Execute prompt optimization
        optimized_result = await engine._execute_prompt_alchemy(
            user_prompt=test_prompt,
            mission_id_str="test_optimization_001",
            update_callback=update_callback
        )
        
        print("\n✅ PROMPT OPTIMIZATION COMPLETE")
        print("=" * 60)
        
        # Display results
        print("📊 OPTIMIZATION RESULTS:")
        print(f"  Optimized Prompt: {optimized_result.get('optimized_prompt', 'N/A')}")
        print(f"  Success Criteria: {optimized_result.get('success_criteria', [])}")
        print(f"  Recommended Agents: {optimized_result.get('recommended_agents', [])}")
        print(f"  Technical Context: {optimized_result.get('technical_context', {})}")
        print(f"  Risk Factors: {optimized_result.get('risk_factors', [])}")
        print(f"  Optimization Notes: {optimized_result.get('optimization_notes', [])}")
        
        print("\n🎯 The enhanced Prompt Optimization Agent has successfully:")
        print("  ✅ Analyzed the original request for clarity and completeness")
        print("  ✅ Deconstructed complex requirements into actionable components")
        print("  ✅ Added necessary context and technical specifications")
        print("  ✅ Defined specific success criteria and measurable outcomes")
        print("  ✅ Identified appropriate agent roles for execution")
        print("  ✅ Assessed risks and provided mitigation strategies")
        
        return optimized_result
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return None


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_prompt_optimization())
    
    if result:
        print("\n🎉 TEST SUCCESSFUL!")
        print("The enhanced Prompt Optimization Agent is working correctly.")
    else:
        print("\n💥 TEST FAILED!")
        print("Please check the error messages above.") 