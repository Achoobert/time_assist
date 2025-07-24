#!/usr/bin/env python3
"""
LLM Integration for Reporter App
Sends daily work logs to local LLM for processing into standup reports
"""

import requests
import yaml
import json
from pathlib import Path
from datetime import datetime

def get_llm_config():
    """Load LLM configuration from context.yml"""
    try:
        context_file = Path(__file__).parent.parent / 'context.yml'
        if context_file.exists():
            with open(context_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                return data.get('local_llm', {})
    except Exception as e:
        print(f"Error loading LLM config: {e}")
    
    return {}

def process_worklog_with_llm(worklog_text):
    """Send worklog to LLM and return processed standup report"""
    config = get_llm_config()
    
    if not config.get('enabled', False):
        return "LLM processing is disabled in context.yml"
    
    api_url = config.get('api', 'http://localhost:11434/api/generate')
    model = config.get('model', 'llama3:8b')
    prompt = config.get('prompt', 'Convert these work logs into a daily standup report. Only return the report:')
    chunk_size = config.get('chunk_size', 4000)
    
    # Prepare the full prompt
    full_prompt = f"{prompt}\n\nWork logs:\n{worklog_text}"
    
    # Chunk the text if it's too long
    if len(full_prompt) > chunk_size:
        # Take the most recent entries (end of the log)
        truncated_logs = worklog_text[-chunk_size + len(prompt) - 100:]
        full_prompt = f"{prompt}\n\nWork logs (most recent):\n{truncated_logs}"
    
    # Prepare request payload for Ollama API
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', 'No response from LLM')
        
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to LLM API. Make sure Ollama is running:\n\nRun: ollama run llama3:8b"
    except requests.exceptions.Timeout:
        return "❌ LLM request timed out. The model might be loading..."
    except requests.exceptions.RequestException as e:
        return f"❌ LLM API error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"

def start_llm_if_needed():
    """Attempt to start the LLM if it's not running"""
    config = get_llm_config()
    start_command = config.get('start_command', 'ollama run llama3:8b')
    
    # This is informational - the user needs to run this manually
    return f"To start the LLM, run: {start_command}"

if __name__ == '__main__':
    # Test the LLM functionality
    test_log = """2025-01-24 09:00 [TestOrg] [123# fix bug] - Fixed authentication issue
2025-01-24 10:30 [TestOrg] [456# new feature] - Implemented user dashboard
2025-01-24 14:00 [Personal] [] - Code review and documentation"""
    
    result = process_worklog_with_llm(test_log)
    print("LLM Result:")
    print(result)
