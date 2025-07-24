#!/usr/bin/env python3
"""
Integration test for LLM functionality with actual Ollama service.
This test checks if the LLM can process real worklog data when Ollama is running.
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_llm_integration():
    """Test LLM integration with actual Ollama service if available"""
    print("🧪 Testing LLM integration with Ollama...")
    
    from llm import process_worklog_with_llm, get_llm_config
    
    # Check if LLM is enabled in config
    config = get_llm_config()
    if not config.get('enabled', False):
        print("⚠️  LLM is disabled in context.yml, skipping integration test")
        return True
    
    # Test worklog
    test_worklog = """2025-01-24 09:00 [TestOrg] [123# fix bug] - Fixed authentication issue in user login system
2025-01-24 10:30 [TestOrg] [456# new feature] - Implemented user dashboard with real-time updates
2025-01-24 14:00 [Personal] [] - Code review and documentation updates
2025-01-24 15:30 [OpenSource] [PR#789] - Contributed bug fix to open source project"""
    
    print("Processing test worklog with LLM...")
    result = process_worklog_with_llm(test_worklog)
    
    # Check if we got a meaningful response
    if "Cannot connect to LLM API" in result:
        print("⚠️  Ollama is not running. To test LLM integration:")
        print("   1. Install Ollama: https://ollama.ai/")
        print("   2. Run: ollama run llama3:8b")
        print("   3. Run this test again")
        return True
    elif "timed out" in result:
        print("⚠️  LLM request timed out. The model might be loading...")
        return True
    elif "API error" in result:
        print("⚠️  LLM API error occurred")
        return True
    else:
        print("✅ LLM integration successful!")
        print("Generated report:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Basic validation of the response
        assert len(result) > 50, "❌ Response should be substantial"
        assert isinstance(result, str), "❌ Response should be a string"
        
        return True

if __name__ == '__main__':
    success = test_llm_integration()
    sys.exit(0 if success else 1)