# there should be a pyQT dashboard that has these panels
# Display open issues, PRS, reviews, etc. 
# display logged work for current day from text file, with button to copy to clipboard
#  select options, and text Field to input new work-log. Reload ui on save
# button to  refresh github data, link to context.yml dashboards

import sys
import os
import re
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
            self.setStyleSheet("color: blue; text-decoration: underline; padding: 4px; border-bottom: 1px solid #eee;")
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
        with open(log_file, 'a') as f:
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
        self.init_ui()
        
        # Set up auto-refresh timer for GitHub data
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_github_data)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes

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
        self.worklog_text.setStyleSheet("font-family: monospace; font-size: 11px;")
        worklog_layout.addWidget(self.worklog_text)
        layout.addLayout(worklog_layout)

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
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(context_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

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
        """When window gets focus, focus the entry field"""
        super().focusInEvent(event)
        self.entry_field.setFocus()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            self.entry_field.setFocus()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if not self.entry_field.hasFocus():
                self.entry_field.setFocus()
        super().keyPressEvent(event)

    def copy_worklog(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.worklog_text.toPlainText())
        QMessageBox.information(self, 'Copied', 'Work log copied to clipboard!')

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())
