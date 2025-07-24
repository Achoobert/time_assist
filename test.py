#!/usr/bin/env python3
"""
Convenience script to run all Reporter app tests from project root.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the consolidated test suite"""
    test_runner = Path(__file__).parent / 'scripts' / 'tests' / 'run_all_tests.py'
    
    if not test_runner.exists():
        print("❌ Test runner not found!")
        return 1
    
    try:
        # Run the test suite
        result = subprocess.run([sys.executable, str(test_runner)], 
                              cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())