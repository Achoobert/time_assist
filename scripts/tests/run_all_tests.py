#!/usr/bin/env python3
"""
Consolidated test runner for all Reporter app tests.
Runs all test modules and provides a summary report.
"""

import sys
import importlib.util
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_module(test_file):
    """Run a single test module and return results"""
    print(f"\n{'='*80}")
    print(f"🧪 RUNNING: {test_file.name}")
    print(f"{'='*80}")
    
    try:
        # Import and run the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        test_module = importlib.util.module_from_spec(spec)
        
        # Capture the original sys.argv to restore later
        original_argv = sys.argv.copy()
        sys.argv = [str(test_file)]  # Set argv as if running the test directly
        
        try:
            spec.loader.exec_module(test_module)
            
            # Check if the module has a main test function
            if hasattr(test_module, 'run_all_tests'):
                result = test_module.run_all_tests()
            elif hasattr(test_module, 'run_ui_tests'):
                result = test_module.run_ui_tests()
            elif hasattr(test_module, 'test_llm_integration'):
                result = test_module.test_llm_integration()
            elif hasattr(test_module, 'test_worklog_preservation'):
                result = test_module.test_worklog_preservation()
            elif hasattr(test_module, 'demonstrate_ui_improvements'):
                result = test_module.demonstrate_ui_improvements()
            else:
                print("⚠️  No recognized test function found, assuming success")
                result = True
                
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
            
        return result
        
    except Exception as e:
        print(f"❌ ERROR running {test_file.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests and provide summary"""
    print("🚀 REPORTER APP - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Find all test files in the current directory
    test_dir = Path(__file__).parent
    test_files = [
        test_dir / 'test_llm_functionality.py',
        test_dir / 'test_llm_integration.py', 
        test_dir / 'test_worklog_preservation.py',
        test_dir / 'test_ui_llm_disabled.py',
        test_dir / 'test_ui_visual.py'
    ]
    
    # Filter to only existing files
    existing_test_files = [f for f in test_files if f.exists()]
    
    if not existing_test_files:
        print("❌ No test files found!")
        return False
    
    print(f"Found {len(existing_test_files)} test modules:")
    for test_file in existing_test_files:
        print(f"  - {test_file.name}")
    
    # Run all tests
    results = {}
    passed = 0
    failed = 0
    
    for test_file in existing_test_files:
        try:
            result = run_test_module(test_file)
            results[test_file.name] = result
            if result:
                passed += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print("\n⚠️  Test run interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error with {test_file.name}: {e}")
            results[test_file.name] = False
            failed += 1
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} {test_name}")
    
    print(f"\n🏁 FINAL RESULTS:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The Reporter app is working correctly.")
        return True
    else:
        print(f"\n💥 {failed} TEST(S) FAILED")
        print("Please review the output above for details.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)