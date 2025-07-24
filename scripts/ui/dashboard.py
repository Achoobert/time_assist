# there should be a pyQT dashboard that has these panels
# Display open issues, PRS, reviews, etc. 
# display logged work for current day from text file, with button to copy to clipboard
#  select options, and text Field to input new work-log. Reload ui on save
# button to  refresh github data, link to context.yml dashboards

import sys
import os
import re
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QLineEdit, QTabWidget, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QCursor

# Custom clickable label widget
class ClickableLabel(QLabel):
    def __init__(self, text, url=None):
        super().__init__(text)
        self.url = url
        if url:
            self.setStyleSheet("color: aqua; text-decoration: underline; padding: 4px; border-bottom: 1px solid #eee;")
            self.setCursor(QCursor(Qt.PointingHandCursor))
        else:
            self.setStyleSheet("padding: 4px; border-bottom: 1px solid #eee;")
        self.setWordWrap(True)
    
    def mousePressEvent(self, event):
        if self.url and event.button() == Qt.LeftButton:
            webbrowser.open(self.url)
        super().mousePressEvent(event)

# Data functions

def get_data_dir():
    """Get or create the ~/.reporter data directory"""
    data_dir = Path.home() / '.reporter'
    data_dir.mkdir(exist_ok=True)
    return data_dir

def extract_url_from_text(text):
    """Extract URL from text like 'title [https://github.com/...]'"""
    url_match = re.search(r'\[([^\]]+)\]', text)
    if url_match:
        url = url_match.group(1)
        # Clean text by removing the URL part
        clean_text = re.sub(r'\s*\[([^\]]+)\]', '', text)
        return clean_text.strip(), url
    return text, None

def get_github_data():
    """Load GitHub data from YAML file and return with URLs extracted"""
    try:
        import yaml
        
        # Try multiple locations for the GitHub data file
        possible_locations = [
            get_data_dir() / 'github_data.yml',  # User's home directory
            Path(__file__).parent.parent.parent / 'user_data' / 'github_data.yml',  # Project directory
            Path.cwd() / 'user_data' / 'github_data.yml',  # Current working directory
        ]
        
        for github_file in possible_locations:
            if github_file.exists():
                with open(github_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    
                    result = {'issues': [], 'prs': [], 'reviews': []}
                    
                    # Process issues
                    for k, v in data.get('my_issues', {}).items():
                        text, url = extract_url_from_text(v)
                        result['issues'].append({
                            'text': f"#{k}: {text}",
                            'url': url,
                            'raw': f"#{k}: {v}"  # For combo box
                        })
                    
                    # Process PRs
                    for k, v in data.get('my_prs', {}).items():
                        text, url = extract_url_from_text(v)
                        result['prs'].append({
                            'text': f"#{k}: {text}",
                            'url': url,
                            'raw': f"#{k}: {v}"  # For combo box
                        })
                    
                    # Process reviews
                    for k, v in data.get('my_reviews', {}).items():
                        text, url = extract_url_from_text(v)
                        result['reviews'].append({
                            'text': f"#{k}: {text}",
                            'url': url,
                            'raw': f"#{k}: {v}"  # For combo box
                        })
                    
                    return result
                    
    except Exception as e:
        print(f"Error loading GitHub data: {e}")
    
    return {
        'issues': [{'text': 'No GitHub data available', 'url': None, 'raw': 'No GitHub data available'}],
        'prs': [{'text': 'No GitHub data available', 'url': None, 'raw': 'No GitHub data available'}],
        'reviews': [{'text': 'No GitHub data available', 'url': None, 'raw': 'No GitHub data available'}],
    }

def get_organizations():
    """Get list of organizations/projects from context.yml"""
    try:
        import yaml
        
        # Try multiple locations for context.yml
        possible_locations = [
            Path(__file__).parent.parent.parent / 'context.yml',  # Project directory
            Path.cwd() / 'context.yml',  # Current working directory
        ]
        
        for context_file in possible_locations:
            if context_file.exists():
                with open(context_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    projects = data.get('projects', {})
                    return list(projects.keys()) + ['Personal', 'Other']
                    
    except Exception as e:
        print(f"Error loading organizations: {e}")
    
    return ['Personal', 'Work', 'Other']

def get_today_worklog():
    """Load today's work log from file"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = get_data_dir() / f'worklog_{today}.txt'
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading worklog: {e}")
    
    return f"Work log for {today}:\n(No entries yet)"

def save_worklog_entry(organization, issue, entry_text):
    """Save a work log entry with organization and issue context"""
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now().strftime('%H:%M')
    log_file = get_data_dir() / f'worklog_{today}.txt'
    
    # Format: YYYY-MM-DD HH:MM [Organization] [Issue] - Entry
    org_part = f"[{organization}]" if organization and organization != "Select organization..." else ""
    issue_part = f"[{issue}]" if issue and issue != "Select issue/PR..." else ""
    
    log_entry = f"{today} {now} {org_part} {issue_part} - {entry_text}\n"
    
    try:
        # CRITICAL: Always use append mode ('a') to preserve existing work log entries
        # Never use 'w' mode which would overwrite/erase previous entries
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        return True
    except Exception as e:
        print(f"Error saving worklog entry: {e}")
        return False

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Reporter - Work Tracker')
        self.resize(900, 700)
        self.organizations = get_organizations()
        self.github_data = get_github_data()
        self.llm_enabled = False  # Initialize before init_ui
        self.init_ui()
        
        # Auto-refresh disabled to prevent interrupting user input
        # Users can manually refresh GitHub data when needed

    def init_ui(self):
        layout = QVBoxLayout()

        # Work Entry Section (Top Priority - Autofocus)
        entry_section = QVBoxLayout()
        entry_label = QLabel('Quick Work Entry:')
        entry_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        entry_section.addWidget(entry_label)

        # Organization/Project Selection
        org_layout = QHBoxLayout()
        org_layout.addWidget(QLabel('Organization:'))
        self.org_combo = QComboBox()
        self.org_combo.addItem("Select organization...")
        self.org_combo.addItems(self.organizations)
        self.org_combo.setCurrentIndex(0)
        org_layout.addWidget(self.org_combo)
        entry_section.addLayout(org_layout)

        # GitHub Issue/PR Selection
        issue_layout = QHBoxLayout()
        issue_layout.addWidget(QLabel('Issue/PR:'))
        self.issue_combo = QComboBox()
        self.issue_combo.addItem("Select issue/PR...")
        self.update_issue_combo()
        issue_layout.addWidget(self.issue_combo)
        entry_section.addLayout(issue_layout)

        # Main text entry (AUTOFOCUS)
        self.entry_field = QLineEdit()
        self.entry_field.setPlaceholderText('Enter work description... (Press Enter to save)')
        self.entry_field.returnPressed.connect(self.save_entry)
        self.entry_field.setStyleSheet("padding: 8px; font-size: 12px;")
        entry_section.addWidget(self.entry_field)

        # Save button
        save_btn = QPushButton('Save Entry (Enter)')
        save_btn.clicked.connect(self.save_entry)
        save_btn.setStyleSheet("padding: 6px;")
        entry_section.addWidget(save_btn)

        layout.addLayout(entry_section)

        # Separator
        layout.addWidget(QLabel("─" * 80))

        # Today's Work Log Panel
        worklog_layout = QVBoxLayout()
        worklog_header = QHBoxLayout()
        worklog_label = QLabel('Today\'s Work Log:')
        worklog_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        copy_btn = QPushButton('Copy to Clipboard')
        copy_btn.clicked.connect(self.copy_worklog)
        copy_btn.setStyleSheet("padding: 4px 12px;")
        worklog_header.addWidget(worklog_label)
        worklog_header.addStretch()
        worklog_header.addWidget(copy_btn)
        worklog_layout.addLayout(worklog_header)

        self.worklog_text = QTextEdit()
        self.worklog_text.setReadOnly(True)
        self.worklog_text.setText(get_today_worklog())
        self.worklog_text.setStyleSheet("font-family: monospace; font-size: 11px; color: black; background-color: white;")
        worklog_layout.addWidget(self.worklog_text)
        layout.addLayout(worklog_layout)

        # LLM Report Panel (only show if LLM is enabled)
        self.llm_enabled = self.is_llm_enabled()
        if self.llm_enabled:
            llm_layout = QVBoxLayout()
            llm_header = QHBoxLayout()
            llm_label = QLabel('LLM Generated Standup Report:')
            llm_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            
            # Move Generate button to LLM section
            llm_btn = QPushButton('Generate LLM Report')
            llm_btn.clicked.connect(self.generate_llm_report)
            llm_btn.setStyleSheet("padding: 4px 12px; background-color: #4CAF50; color: white;")
            
            copy_llm_btn = QPushButton('Copy LLM Report')
            copy_llm_btn.clicked.connect(self.copy_llm_report)
            copy_llm_btn.setStyleSheet("padding: 4px 12px;")
            
            llm_header.addWidget(llm_label)
            llm_header.addStretch()
            llm_header.addWidget(llm_btn)
            llm_header.addWidget(copy_llm_btn)
            llm_layout.addLayout(llm_header)

            self.llm_text = QTextEdit()
            self.llm_text.setReadOnly(True)
            self.llm_text.setPlaceholderText("Click 'Generate LLM Report' to process your work log with AI...")
            # Fix text visibility with proper colors
            self.llm_text.setStyleSheet("font-family: system; font-size: 12px; color: black; background-color: #f8f9fa; border: 1px solid #ddd;")
            llm_layout.addWidget(self.llm_text)
            layout.addLayout(llm_layout)

        # GitHub Data Panel (Collapsible)
        self.github_panel = QTabWidget()
        self.create_github_tabs()
        layout.addWidget(self.github_panel)

        # Control buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('Refresh GitHub Data')
        refresh_btn.clicked.connect(self.refresh_github_data)
        context_btn = QPushButton('Open context.yml')
        context_btn.clicked.connect(self.open_context_yml)
        open_data_btn = QPushButton('Open Data Directory')
        open_data_btn.clicked.connect(self.open_data_directory)
        copy_path_btn = QPushButton('Copy Data Path')
        copy_path_btn.clicked.connect(self.copy_data_path)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(context_btn)
        btn_layout.addWidget(open_data_btn)
        btn_layout.addWidget(copy_path_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def is_llm_enabled(self):
        """Check if LLM is enabled in context.yml"""
        try:
            import yaml
            
            # Try multiple locations for context.yml
            possible_locations = [
                Path(__file__).parent.parent.parent / 'context.yml',  # Project directory
                Path.cwd() / 'context.yml',  # Current working directory
            ]
            
            for context_file in possible_locations:
                if context_file.exists():
                    with open(context_file, 'r') as f:
                        data = yaml.safe_load(f) or {}
                        llm_config = data.get('local_llm', {})
                        return llm_config.get('enabled', False)
                        
        except Exception as e:
            print(f"Error checking LLM config: {e}")
        
        return False

    def create_github_tabs(self):
        """Create GitHub data tabs with clickable links"""
        for key, items in self.github_data.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            for item in items:
                if isinstance(item, dict):
                    # New format with text and URL
                    label = ClickableLabel(item['text'], item['url'])
                else:
                    # Fallback for old format
                    label = ClickableLabel(str(item))
                tab_layout.addWidget(label)
            
            tab_layout.addStretch()
            tab.setLayout(tab_layout)
            self.github_panel.addTab(tab, key.capitalize())

    def update_issue_combo(self):
        """Update issue combo box with all GitHub issues and PRs"""
        self.issue_combo.clear()
        self.issue_combo.addItem("Select issue/PR...")
        
        # Add all issues and PRs
        for item in self.github_data.get('issues', []):
            if isinstance(item, dict):
                if item['text'] != 'No GitHub data available':
                    self.issue_combo.addItem(f"Issue: {item['text']}")
            elif item != 'No GitHub data available':
                self.issue_combo.addItem(f"Issue: {item}")
        
        for item in self.github_data.get('prs', []):
            if isinstance(item, dict):
                if item['text'] != 'No GitHub data available':
                    self.issue_combo.addItem(f"PR: {item['text']}")
            elif item != 'No GitHub data available':
                self.issue_combo.addItem(f"PR: {item}")
        
        for item in self.github_data.get('reviews', []):
            if isinstance(item, dict):
                if item['text'] != 'No GitHub data available':
                    self.issue_combo.addItem(f"Review: {item['text']}")
            elif item != 'No GitHub data available':
                self.issue_combo.addItem(f"Review: {item}")

    def focusInEvent(self, event):
        """When window gets focus, focus the entry field only if no other widget has focus"""
        super().focusInEvent(event)
        # Only auto-focus if no widget currently has focus
        if not self.focusWidget():
            self.entry_field.setFocus()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            # Escape always returns focus to entry field
            self.entry_field.setFocus()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Only redirect Enter to entry field if it's not already focused
            # and if we're not in a combo box or other input widget
            focused_widget = self.focusWidget()
            if (not self.entry_field.hasFocus() and 
                not isinstance(focused_widget, (QComboBox, QTextEdit))):
                self.entry_field.setFocus()
        super().keyPressEvent(event)

    def copy_worklog(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.worklog_text.toPlainText())
        QMessageBox.information(self, 'Copied', 'Work log copied to clipboard!')

    def copy_llm_report(self):
        if not self.llm_enabled or not hasattr(self, 'llm_text'):
            QMessageBox.information(self, 'LLM Disabled', 'LLM functionality is disabled in context.yml')
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(self.llm_text.toPlainText())
        QMessageBox.information(self, 'Copied', 'LLM report copied to clipboard!')

    def generate_llm_report(self):
        """Generate LLM standup report from today's work log"""
        if not self.llm_enabled:
            QMessageBox.information(self, 'LLM Disabled', 'LLM functionality is disabled in context.yml')
            return
            
        try:
            # Import LLM functionality
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from llm import process_worklog_with_llm
            
            # Get current work log text
            worklog_content = self.worklog_text.toPlainText()
            
            if not worklog_content or "No entries yet" in worklog_content:
                QMessageBox.warning(self, 'No Data', 'No work log entries to process.')
                return
            
            # Show processing message
            if hasattr(self, 'llm_text'):
                self.llm_text.setText("🤖 Processing work log with LLM... This may take a moment...")
                QApplication.processEvents()  # Update UI immediately
            
            # Process with LLM
            llm_result = process_worklog_with_llm(worklog_content)
            
            # Display result
            if hasattr(self, 'llm_text'):
                self.llm_text.setText(llm_result)
            
        except ImportError as e:
            if hasattr(self, 'llm_text'):
                self.llm_text.setText(f"❌ LLM module not available: {e}")
            else:
                QMessageBox.warning(self, 'Error', f"LLM module not available: {e}")
        except Exception as e:
            if hasattr(self, 'llm_text'):
                self.llm_text.setText(f"❌ Error generating LLM report: {e}")
            else:
                QMessageBox.warning(self, 'Error', f"Error generating LLM report: {e}")

    def save_entry(self):
        entry_text = self.entry_field.text().strip()
        if not entry_text:
            QMessageBox.warning(self, 'Empty Entry', 'Please enter some work description.')
            return

        # Get selected organization and issue
        organization = self.org_combo.currentText()
        if organization == "Select organization...":
            organization = ""
        
        issue = self.issue_combo.currentText()
        if issue == "Select issue/PR...":
            issue = ""
        else:
            # Clean up the issue text (remove "Issue: " or "PR: " prefix)
            issue = issue.replace("Issue: ", "").replace("PR: ", "").replace("Review: ", "")

        # Save the entry
        if save_worklog_entry(organization, issue, entry_text):
            # Clear the entry field and refresh the log
            self.entry_field.clear()
            self.worklog_text.setText(get_today_worklog())
            
            # Keep focus on entry field for next entry
            self.entry_field.setFocus()
            
            # Optional: Reset selections for next entry
            # self.org_combo.setCurrentIndex(0)
            # self.issue_combo.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, 'Error', 'Failed to save entry.')

    def refresh_github_data(self):
        """Refresh GitHub data by calling the github_data module directly"""
        try:
            # Save current user input and selections to preserve them
            current_text = self.entry_field.text()
            current_org = self.org_combo.currentText()
            current_issue = self.issue_combo.currentText()
            
            # Import and run the github_data module directly
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from github_data import main as github_main
            
            # Run the GitHub data collection
            github_main()
            
            # Reload the GitHub data
            self.github_data = get_github_data()
            self.update_issue_combo()
            
            # Refresh the GitHub tabs
            self.refresh_github_tabs()
            
            # Restore user input and selections
            self.entry_field.setText(current_text)
            
            # Restore organization selection if it still exists
            org_index = self.org_combo.findText(current_org)
            if org_index >= 0:
                self.org_combo.setCurrentIndex(org_index)
            
            # Restore issue selection if it still exists
            issue_index = self.issue_combo.findText(current_issue)
            if issue_index >= 0:
                self.issue_combo.setCurrentIndex(issue_index)
            
            # Keep focus on entry field
            self.entry_field.setFocus()
            
            QMessageBox.information(self, 'Success', 'GitHub data refreshed successfully!')
                
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Error refreshing GitHub data: {e}')

    def refresh_github_tabs(self):
        """Refresh the GitHub data tabs with new data"""
        # Clear existing tabs
        self.github_panel.clear()
        
        # Recreate tabs with new data using clickable labels
        self.create_github_tabs()

    def open_context_yml(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../context.yml'))
        if os.path.exists(path):
            os.system(f'open "{path}"')
        else:
            QMessageBox.warning(self, 'Not found', 'context.yml not found.')

    def open_data_directory(self):
        """Open the data directory where worklog files are stored"""
        data_dir = get_data_dir()
        
        # Create the directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        
        # Open the directory in Finder (macOS) or file explorer
        try:
            subprocess.run(['open', str(data_dir)], check=True)
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, 'Error', 'Could not open directory.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open directory: {e}')

    def copy_data_path(self):
        """Copy the data directory path to clipboard"""
        data_dir = get_data_dir()
        
        # Create the directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        
        # Copy the path to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(str(data_dir))
        QMessageBox.information(self, 'Copied', f'Data directory path copied to clipboard:\n{data_dir}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
