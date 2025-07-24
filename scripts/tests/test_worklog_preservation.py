#!/usr/bin/env python3
"""
Test script to verify work log files are never erased or overwritten.
This ensures user data is always preserved.
"""

import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_worklog_preservation():
    """Test that work log entries are always appended, never overwritten"""
    
    # Import the dashboard functions
    from ui.dashboard import save_worklog_entry, get_today_worklog, get_data_dir
    
    print("🧪 Testing work log preservation...")
    
    # Create a temporary directory for testing
    original_data_dir = get_data_dir()
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Temporarily override the data directory
        import ui.dashboard
        ui.dashboard.get_data_dir = lambda: temp_dir
        
        # Test 1: Save first entry
        result1 = save_worklog_entry("TestOrg", "123# test issue", "First work entry")
        assert result1, "❌ Failed to save first entry"
        
        # Verify first entry exists
        worklog_content = get_today_worklog()
        assert "First work entry" in worklog_content, "❌ First entry not found"
        print("✅ First entry saved successfully")
        
        # Test 2: Save second entry (should append, not overwrite)
        result2 = save_worklog_entry("AnotherOrg", "456# another issue", "Second work entry")
        assert result2, "❌ Failed to save second entry"
        
        # Verify both entries exist
        worklog_content = get_today_worklog()
        assert "First work entry" in worklog_content, "❌ First entry was erased!"
        assert "Second work entry" in worklog_content, "❌ Second entry not found"
        print("✅ Second entry appended successfully - first entry preserved")
        
        # Test 3: Save third entry with different formatting
        result3 = save_worklog_entry("", "", "Third entry without org/issue")
        assert result3, "❌ Failed to save third entry"
        
        # Verify all three entries exist
        worklog_content = get_today_worklog()
        assert "First work entry" in worklog_content, "❌ First entry was erased!"
        assert "Second work entry" in worklog_content, "❌ Second entry was erased!"
        assert "Third entry without org/issue" in worklog_content, "❌ Third entry not found"
        print("✅ Third entry appended successfully - all previous entries preserved")
        
        # Test 4: Verify file structure
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = temp_dir / f'worklog_{today}.txt'
        assert log_file.exists(), "❌ Work log file doesn't exist"
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3, f"❌ Expected 3 lines, got {len(lines)}"
        assert all("First work entry" in line or "Second work entry" in line or "Third entry without org/issue" in line for line in lines), "❌ Not all entries found in file"
        print("✅ Work log file structure verified")
        
        print("🎉 ALL TESTS PASSED - Work log entries are never erased!")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    success = test_worklog_preservation()
    sys.exit(0 if success else 1)