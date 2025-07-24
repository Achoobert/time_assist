#!/usr/bin/env python3
"""
Reporter - Main Application Entry Point
Track your work in 25-minute increments and generate daily standup reports.
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def main():
    parser = argparse.ArgumentParser(description='Reporter - Work tracking and standup report generator')
    parser.add_argument('--cli', choices=['github', 'worklog'], 
                       help='Run in CLI mode (github: collect GitHub data, worklog: manage work logs)')
    
    args = parser.parse_args()
    
    if args.cli == 'github':
        # Run GitHub data collection
        try:
            from github_data import main as github_main
            github_main()
        except ImportError as e:
            print(f"Error importing GitHub data module: {e}")
            sys.exit(1)
    elif args.cli == 'worklog':
        # Future: worklog CLI functionality
        print("Worklog CLI functionality coming soon!")
    else:
        # Default: Launch PyQt GUI
        try:
            from PyQt5.QtWidgets import QApplication
            from ui.dashboard import Dashboard
            
            app = QApplication(sys.argv)
            app.setApplicationName('Reporter')
            app.setApplicationDisplayName('Reporter - Work Tracker')
            
            # Set focus policy for autofocus behavior (only if attribute exists)
            if hasattr(app, 'AA_MacDontSwapCtrlAndMeta'):
                app.setAttribute(app.AA_MacDontSwapCtrlAndMeta, True)
            
            dashboard = Dashboard()
            dashboard.show()
            
            # Ensure the input field gets focus when app starts
            dashboard.entry_field.setFocus()
            
            sys.exit(app.exec_())
            
        except ImportError as e:
            print(f"Error importing PyQt5 or dashboard: {e}")
            print("Make sure PyQt5 is installed: pip install PyQt5")
            sys.exit(1)
        except Exception as e:
            print(f"Error launching GUI: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()